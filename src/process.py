import json
import math
import os
import sys
import warnings

import torch
import numpy as np
from PIL import Image, ImageFilter, ImageOps
import random
import cv2
from skimage import exposure
from typing import Any, Dict, List, Optional

import modules.sd_hijack
from modules import devices, prompt_parser, masking, sd_samplers, lowvram, generation_parameters_copypaste, script_callbacks
from modules.sd_hijack import model_hijack
from modules.shared import opts, cmd_opts, state
import modules.shared as shared
import modules.face_restoration
import modules.images as images
import modules.styles
import modules.sd_models as sd_models
import modules.sd_vae as sd_vae
import logging
from ldm.data.util import AddMiDaS
from ldm.models.diffusion.ddpm import LatentDepth2ImageDiffusion

from einops import repeat, rearrange
from blendmodes.blend import blendLayers, BlendType
from modules.processing import StableDiffusionProcessing


class StableDiffusionProcessingImg2Img(StableDiffusionProcessing):
    sampler = None

    def __init__(self, init_images: list = None, resize_mode: int = 0, denoising_strength: float = 0.75, mask: Any = None, mask_blur: int = 4, inpainting_fill: int = 0, inpaint_full_res: bool = True, inpaint_full_res_padding: int = 0, inpainting_mask_invert: int = 0, initial_noise_multiplier: float = None, **kwargs):
        super().__init__(**kwargs)

        self.init_images = init_images
        self.resize_mode: int = resize_mode
        self.denoising_strength: float = denoising_strength
        self.init_latent = None
        self.image_mask = mask
        self.latent_mask = None
        self.mask_for_overlay = None
        self.mask_blur = mask_blur
        self.inpainting_fill = inpainting_fill
        self.inpaint_full_res = inpaint_full_res
        self.inpaint_full_res_padding = inpaint_full_res_padding
        self.inpainting_mask_invert = inpainting_mask_invert
        self.initial_noise_multiplier = opts.initial_noise_multiplier if initial_noise_multiplier is None else initial_noise_multiplier
        self.mask = None
        self.nmask = None
        self.image_conditioning = None

    def init(self, all_prompts, all_seeds, all_subseeds):
        self.sampler = sd_samplers.create_sampler(self.sampler_name, self.sd_model)
        # crop_region = None
        #
        # image_mask = self.image_mask
        #
        # if image_mask is not None:
        #     image_mask = image_mask.convert('L')
        #
        #     if self.inpainting_mask_invert:
        #         image_mask = ImageOps.invert(image_mask)
        #
        #     if self.mask_blur > 0:
        #         image_mask = image_mask.filter(ImageFilter.GaussianBlur(self.mask_blur))
        #
        #     if self.inpaint_full_res:
        #         self.mask_for_overlay = image_mask
        #         mask = image_mask.convert('L')
        #         crop_region = masking.get_crop_region(np.array(mask), self.inpaint_full_res_padding)
        #         crop_region = masking.expand_crop_region(crop_region, self.width, self.height, mask.width, mask.height)
        #         x1, y1, x2, y2 = crop_region
        #
        #         mask = mask.crop(crop_region)
        #         image_mask = images.resize_image(2, mask, self.width, self.height)
        #         self.paste_to = (x1, y1, x2-x1, y2-y1)
        #     else:
        #         image_mask = images.resize_image(self.resize_mode, image_mask, self.width, self.height)
        #         np_mask = np.array(image_mask)
        #         np_mask = np.clip((np_mask.astype(np.float32)) * 2, 0, 255).astype(np.uint8)
        #         self.mask_for_overlay = Image.fromarray(np_mask)
        #
        #     self.overlay_images = []

        # latent_mask = self.latent_mask if self.latent_mask is not None else image_mask

        # add_color_corrections = opts.img2img_color_correction and self.color_corrections is None
        # if add_color_corrections:
        #     self.color_corrections = []
        imgs = []
        for image in self.init_images:
            if isinstance(image, Image.Image):
                image = images.flatten(image, opts.img2img_background_color)
                image = np.array(image).astype(np.float32) / 255.0
                image = np.moveaxis(image, 2, 0)

            imgs.append(image)
            #
            # if crop_region is None and self.resize_mode != 3:
            #     image = images.resize_image(self.resize_mode, image, self.width, self.height)
            #
            # if image_mask is not None:
            #     image_masked = Image.new('RGBa', (image.width, image.height))
            #     image_masked.paste(image.convert("RGBA").convert("RGBa"), mask=ImageOps.invert(self.mask_for_overlay.convert('L')))
            #
            #     self.overlay_images.append(image_masked.convert('RGBA'))
            #
            # # crop_region is not None if we are doing inpaint full res
            # if crop_region is not None:
            #     image = image.crop(crop_region)
            #     image = images.resize_image(2, image, self.width, self.height)
            #
            # if image_mask is not None:
            #     if self.inpainting_fill != 1:
            #         image = masking.fill(image, latent_mask)
            #
            # if add_color_corrections:
            #     self.color_corrections.append(setup_color_correction(image))

            # image = np.array(image).astype(np.float32) / 255.0
            # image = np.moveaxis(image, 2, 0)
            #
            # imgs.append(image)

        if len(imgs) == 1:
            batch_images = np.expand_dims(imgs[0], axis=0).repeat(self.batch_size, axis=0)
            # if self.overlay_images is not None:
            #     self.overlay_images = self.overlay_images * self.batch_size
            #
            # if self.color_corrections is not None and len(self.color_corrections) == 1:
            #     self.color_corrections = self.color_corrections * self.batch_size

        elif len(imgs) <= self.batch_size:
            self.batch_size = len(imgs)
            batch_images = np.array(imgs)
        else:
            raise RuntimeError(f"bad number of images passed: {len(imgs)}; expecting {self.batch_size} or less")

        image = torch.from_numpy(batch_images)
        image = 2. * image - 1.
        image = image.to(shared.device)

        self.init_latent = self.sd_model.get_first_stage_encoding(self.sd_model.encode_first_stage(image))

        if self.resize_mode == 3:
            self.init_latent = torch.nn.functional.interpolate(self.init_latent, size=(self.height // opt_f, self.width // opt_f), mode="bilinear")

        # if image_mask is not None:
        #     init_mask = latent_mask
        #     latmask = init_mask.convert('RGB').resize((self.init_latent.shape[3], self.init_latent.shape[2]))
        #     latmask = np.moveaxis(np.array(latmask, dtype=np.float32), 2, 0) / 255
        #     latmask = latmask[0]
        #     latmask = np.around(latmask)
        #     latmask = np.tile(latmask[None], (4, 1, 1))
        #
        #     self.mask = torch.asarray(1.0 - latmask).to(shared.device).type(self.sd_model.dtype)
        #     self.nmask = torch.asarray(latmask).to(shared.device).type(self.sd_model.dtype)
        #
        #     # this needs to be fixed to be done in sample() using actual seeds for batches
        #     if self.inpainting_fill == 2:
        #         self.init_latent = self.init_latent * self.mask + create_random_tensors(self.init_latent.shape[1:], all_seeds[0:self.init_latent.shape[0]]) * self.nmask
        #     elif self.inpainting_fill == 3:
        #         self.init_latent = self.init_latent * self.mask

        # self.image_conditioning = self.img2img_image_conditioning(image, self.init_latent, image_mask)
        self.image_conditioning = self.img2img_image_conditioning(image, self.init_latent, None)

    def sample(self, conditioning, unconditional_conditioning, seeds, subseeds, subseed_strength, prompts):
        x = create_random_tensors([opt_C, self.height // opt_f, self.width // opt_f], seeds=seeds, subseeds=subseeds, subseed_strength=self.subseed_strength, seed_resize_from_h=self.seed_resize_from_h, seed_resize_from_w=self.seed_resize_from_w, p=self)

        if self.initial_noise_multiplier != 1.0:
            self.extra_generation_params["Noise multiplier"] = self.initial_noise_multiplier
            x *= self.initial_noise_multiplier

        samples = self.sampler.sample_img2img(self, self.init_latent, x, conditioning, unconditional_conditioning, image_conditioning=self.image_conditioning)

        if self.mask is not None:
            samples = samples * self.nmask + self.init_latent * self.mask

        del x
        devices.torch_gc()

        return samples
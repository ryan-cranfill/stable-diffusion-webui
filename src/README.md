# Setup 
- clone this repo
- ./webui.sh --xformers
- when it fails, install xformers manually `pip install -v -U git+https://github.com/facebookresearch/xformers.git@main#egg=xformers`
- install triton: 
```
git clone https://github.com/openai/triton.git repositories/triton;
cd repositories/triton/python;
pip install cmake; # build time dependency
pip install -e .
cd -
```
- pip install -r ryan_requirements.txt

# Running
- python -m src.server
- on mac, python -m src.sd_generator --no-half --use-cpu interrogate
- python -m src.display
  - for hot reload, `nodemon --watch src -e py --exec python -m src.display`

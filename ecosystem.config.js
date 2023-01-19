module.exports = {
  /**
   * Application configuration section
   * http://pm2.keymetrics.io/docs/usage/application-declaration/
   */
  apps : [
    {
      name   : "server",
      script : "./venv/bin/python -m src.server",
    },
    {
      name   : "display",
      script : "./venv/bin/python -m src.display",
      env: {
        "DISPLAY": ":0",
      },
      listen_timeout: 30000,
    },
    {
      name   : "generator",
      script : "source webui-user.sh && ./venv/bin/python -m src.sd_generator",
    },
  ]
}
// module.exports = {
//   /**
//    * Application configuration section
//    * http://pm2.keymetrics.io/docs/usage/application-declaration/
//    */
//   apps: [
//
//     // Main API Hosting
//     {
//       name: 'API',
//       script: 'bin/www',
//       env: {
//         COMMON_VARIABLE: 'true'
//       },
//       instances: 1,
//       exec_mode: 'cluster',
//       watch: false,
//       autorestart: true
//     },
//     {
//       name: 'CRON',
//       script: "crons/cronjob.js",
//       instances: 1,
//       exec_mode: 'fork',
//       cron_restart: "0,30 * * * *",
//       watch: false,
//       autorestart: false
//     }
//   ]
// };
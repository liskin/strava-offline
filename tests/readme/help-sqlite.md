    $ strava-offline sqlite --help
    Usage: strava-offline sqlite [OPTIONS]
    
      Synchronize bikes and activities metadata to local sqlite3 database. Unless
      --full is given, the sync is incremental, i.e. only new activities are
      synchronized and deletions aren't detected.
    
    Options:
      Sync options: 
        --full / --no-full    Perform full sync instead of incremental  [default:
                              no-full]
      Strava API: 
        --client-id TEXT      Strava OAuth 2 client id  [env var:
                              STRAVA_CLIENT_ID]
        --client-secret TEXT  Strava OAuth 2 client secret  [env var:
                              STRAVA_CLIENT_SECRET]
        --token-file FILE     Strava OAuth 2 token store  [default:
                              /home/user/.config/strava_offline/token.json]
        --http-host TEXT      OAuth 2 HTTP server host  [default: 127.0.0.1]
        --http-port INTEGER   OAuth 2 HTTP server port  [default: 12345]
      Database: 
        --database FILE       Sqlite database file  [default: /home/user/.local/sh
                              are/strava_offline/strava.sqlite]
      -v, --verbose           Logging verbosity (0 = WARNING, 1 = INFO, 2 = DEBUG)
      --config FILE           Read configuration from FILE.  [default:
                              /home/user/.config/strava_offline/config.yaml]
      --help                  Show this message and exit.

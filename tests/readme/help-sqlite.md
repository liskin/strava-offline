<!--
    $ . "$TESTDIR"/../.xdg-user.sh
-->

    $ strava-offline sqlite --help
    Usage: strava-offline sqlite [OPTIONS]
    
      Synchronize bikes and activities metadata to local sqlite3 database. Unless
      --full is given, the sync is incremental, i.e. only new activities are
      synchronized and deletions aren't detected.
    
      With --source web, metadata is scraped from the Strava website using the
      --strava4-session cookie instead of the (subscription-gated) Strava API.
      Website scraping doesn't provide upload_id.
    
    Options:
      Sync options: 
        --source [api|web]      Metadata source: 'api' (Strava API, needs a Strava
                                subscription) or 'web' (website scraping, needs
                                --strava4-session)  [default: api]
        --full / --no-full      Perform full sync instead of incremental
                                [default: no-full]
      Strava API: 
        --client-id TEXT        Strava OAuth 2 client id  [env var:
                                STRAVA_CLIENT_ID]
        --client-secret TEXT    Strava OAuth 2 client secret  [env var:
                                STRAVA_CLIENT_SECRET]
        --token-file FILE       Strava OAuth 2 token store  [default:
                                /home/user/.config/strava_offline/token.json]
        --http-host TEXT        OAuth 2 HTTP server host  [default: 127.0.0.1]
        --http-port INTEGER     OAuth 2 HTTP server port  [default: 12345]
      Strava web: 
        --strava4-session TEXT  '_strava4_session' cookie value  [env var:
                                STRAVA_COOKIE_STRAVA4_SESSION]
      Database: 
        --database FILE         Sqlite database file  [default: /home/user/.local/
                                share/strava_offline/strava.sqlite]
      -v, --verbose             Logging verbosity (0 = WARNING, 1 = INFO, 2 =
                                DEBUG)
      --config FILE             Read configuration from FILE.  [default:
                                /home/user/.config/strava_offline/config.yaml]
      --help                    Show this message and exit.

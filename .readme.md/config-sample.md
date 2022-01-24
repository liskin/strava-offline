    $ strava-offline --config-sample
    # Perform full sync instead of incremental
    full: false
    
    # Strava OAuth 2 client id
    strava_client_id: '12345'
    
    # Strava OAuth 2 client secret
    strava_client_secret: SECRET
    
    # Strava OAuth 2 token store
    strava_token_filename: /home/user/.config/strava_offline/token.json
    
    # OAuth 2 HTTP server host
    http_host: 127.0.0.1
    
    # OAuth 2 HTTP server port
    http_port: 12345
    
    # Sqlite database file
    strava_sqlite_database: /home/user/.local/share/strava_offline/strava.sqlite
    
    # Logging verbosity (0 = WARNING, 1 = INFO, 2 = DEBUG)
    verbose: 0
    
    # Directory to store gpx files indexed by activity id
    dir_activities: /home/user/.local/share/strava_offline/activities
    
    # Optional path to activities in Strava backup (no need to redownload these)
    dir_activities_backup: DIRECTORY
    
    # '_strava4_session' cookie value
    strava_cookie_strava4_session: TEXT

from waitress import serve
import main
serve(main.app, host='0.0.0.0', port=5000, cleanup_interval=3600,
      channel_timeout=3600, expose_tracebacks=True, threads=32)

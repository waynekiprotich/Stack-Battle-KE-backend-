from app import create_app

# 1. Create the app instance using the factory we defined in app/__init__.py
app = create_app()

if __name__ == '__main__':
    # 2. Start the Flask development server
    # host='0.0.0.0' makes it accessible on your local network
    # port=5000 is the standard Flask port
    # debug=True enables auto-reload when you save files
    print("Stack-Battle KE Backend starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
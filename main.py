import logging

if __name__ == "__main__":
    import uvicorn
    import web_app

    logging.getLogger().setLevel(logging.INFO)

    uvicorn.run(web_app.get_web_app(), host="0.0.0.0", port=8000)

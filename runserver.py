import sys

def main():
    # Load up the webapp module
    from webKickstart import app

    #app.run(host="0.0.0.0", debug=True)
    app.run(debug=True)


if __name__ == "__main__":
    main()


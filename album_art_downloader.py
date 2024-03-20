import typer
import requests
import json
import os
from halo import Halo
import pyfiglet
from InquirerPy import inquirer

app = typer.Typer()

# Create the "AlbumArts" folder if it doesn't exist
if not os.path.exists("AlbumArts"):
    os.makedirs("AlbumArts")

ascii_banner = pyfiglet.figlet_format("Album Art Downloader")
print(ascii_banner)

def get_album_art(album: str, artist: str):
    # Construct the iTunes search API URL
    url = f"https://itunes.apple.com/search?term={artist}+{album}&entity=album&limit=1"

    try:
        # Send a GET request to the iTunes API
        response = requests.get(url)
        response.raise_for_status()

        # Parse the JSON response
        data = json.loads(response.text)

        if data["resultCount"] > 0:
            # Extract the album artwork URL
            artwork_url = data["results"][0]["artworkUrl100"]

            # Replace the dimensions in the URL to get the highest quality
            artwork_url = artwork_url.replace("100x100", "5000x5000")

            # Download the album artwork
            with Halo(text="Downloading album artwork...", spinner="dots"):
                artwork_response = requests.get(artwork_url)
                artwork_response.raise_for_status()

            # Get the file extension from the artwork URL
            file_ext = os.path.splitext(artwork_url)[1]

            # Generate the output filename based on the naming convention
            artist_name = "_".join(artist.split())
            album_name = "_".join(album.split())
            filename = f"{artist_name}-{album_name}-cover{file_ext}"

            # Save the album artwork to the "AlbumArts" folder
            output_path = os.path.join("AlbumArts", filename)
            with open(output_path, "wb") as file:
                file.write(artwork_response.content)

            print(f"Album artwork saved as: {filename}")
        else:
            print("No album artwork found.")

    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {e}")

@app.command()
def main(
    album: str = typer.Option(..., prompt="Enter the album name"),
    artist: str = typer.Option(..., prompt="Enter the artist name")
):
    while True:
        # Call the function to download the album art
        get_album_art(album, artist)

        # Prompt the user for next action
        next_action = inquirer.select(
            message="What would you like to do next?",
            choices=["Download another album art", "Exit"]
        ).execute()

        if next_action == "Exit":
            break
        else:
            # Prompt for new album and artist name
            album = inquirer.text(message="Enter the album name:").execute()
            artist = inquirer.text(message="Enter the artist name:").execute()

if __name__ == "__main__":
    app()

from PIL import Image
import os
import imageio
import moviepy.editor as mp
import shutil
from pytubefix import YouTube


def download_youtube_video(url, output_path):
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension="mp4").order_by("resolution").desc().first()
    if not stream:
        print("Aucun flux vidéo disponible.")
        return None
    mp4_path = os.path.join(output_path, "input.mp4")
    stream.download(output_path, filename="input.mp4")
    print(f"Vidéo téléchargée : {mp4_path}")
    return mp4_path


# Supprimer la limite de taille des images
Image.MAX_IMAGE_PIXELS = None

MAX_WIDTH = 1000000  # Limite maximale supportée par Pillow
MAX_HEIGHT = 1000000  # Limite maximale en hauteur


def clear_folder(folder):
    if os.path.exists(folder):
        shutil.rmtree(folder)
    os.makedirs(folder, exist_ok=True)


def convert_mp4_to_gif(mp4_path, gif_path):
    clip = mp.VideoFileClip(mp4_path)
    clip.write_gif(gif_path, fps=10)  # Modifier le fps si nécessaire
    print(f"GIF enregistré sous {gif_path}")


def extract_frames_from_gif(gif_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    gif = imageio.mimread(gif_path)
    for i, frame in enumerate(gif):
        image = Image.fromarray(frame)
        image.save(os.path.join(output_folder, f"image{i + 1}.jpg"))
    print(f"Images extraites dans {output_folder}")


def assemble_images(output_filename, input_folder):
    images = []
    files = sorted([f for f in os.listdir(input_folder) if f.endswith(".jpg")])

    for file in files:
        file_path = os.path.join(input_folder, file)
        try:
            img = Image.open(file_path)
            images.append(img)
        except Exception as e:
            print(f"Erreur lors de l'ouverture de {file_path}: {e}")

    if not images:
        print("Aucune image valide trouvée.")
        return

    num_images = len(images)
    original_width, original_height = images[0].size
    new_width = MAX_WIDTH // num_images
    new_height = MAX_HEIGHT // num_images

    resized_images = [img.resize((new_width, new_height)) for img in images]
    total_width = sum(img.width for img in resized_images)

    result = Image.new('RGB', (total_width, new_height))

    x_offset = 0
    for img in resized_images:
        result.paste(img, (x_offset, 0))
        x_offset += img.width

    result.save(output_filename, format='PNG')
    print(f"Image assemblée enregistrée sous {output_filename}")


# Exemple d'utilisation
type_source = input("Voulez-vous entrer un lien YouTube (Y) ou un fichier MP4 (M) ? ").strip().lower()
if type_source == "y":
    source = input("Entrez le lien YouTube : ").strip()
elif type_source == "m":
    source = input("Entrez le chemin du fichier MP4 : ").strip()
else:
    print("Choix invalide. Veuillez relancer le script.")
    exit()

output_folder = "frames"
clear_folder(output_folder)

if source.startswith("http"):
    mp4_file = download_youtube_video(source, os.getcwd())
    if not mp4_file:
        print("Échec du téléchargement de la vidéo.")
        exit()
else:
    mp4_file = source

gif_file = "output.gif"
final_image = "output.png"

convert_mp4_to_gif(mp4_file, gif_file)
extract_frames_from_gif(gif_file, output_folder)
assemble_images(final_image, output_folder)


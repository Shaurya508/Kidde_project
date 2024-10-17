import faiss
import torch
from PIL import Image
import matplotlib.pyplot as plt
import clip
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# Load the CLIP model
device = "cpu"
model, preprocess = clip.load("ViT-B/32", device=device)

def get_image_paths(directory: str, number: int = None) -> list:
    """Retrieve image paths from the given directory."""
    image_paths = []
    count = 0
    for filename in os.listdir(directory):
        if filename.endswith('.png'):
            image_paths.append(os.path.join(directory, filename))
            if number is not None and count == number:
                return [image_paths[-1]]
            count += 1
    return image_paths

def retrieve_best_image(text):
    try:
        # Load the FAISS index
        index = faiss.read_index("MMMGPT_mini_Images_Kidde.faiss")
        print("Index loaded successfully.")
        
        # Input query
        query = text
        query_tokens = clip.tokenize([query])  # Tokenize Before Embeddings
        
        # Generate text embeddings for the query
        with torch.no_grad():
            query_embeddings = model.encode_text(query_tokens).float()
        
        # Perform FAISS search (find 1 top match)
        distances, indices = index.search(query_embeddings, 1)
        distances = distances[0]
        indices = indices[0]
        
        # Sort by distance
        indices_distances = list(zip(indices, distances))
        indices_distances.sort(key=lambda x: x[1], reverse=True)

        # Retrieve the best matching image index and distance
        for idx, distance in indices_distances:
            print(f"Best match - Index: {idx}, Distance: {distance}")
            
            # Get image path corresponding to the index
            path = get_image_paths("MMMGPT_Mini_Images/MMMGPT Mini", idx)[0]
            
            # Open and display the image
            im = Image.open(path)
            plt.imshow(im)
            plt.axis('off')
            plt.show()
            return path  # Return the best image path
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage
if __name__ == "__main__":
    text = "What is Budget optimization ?"
    best_image_path = retrieve_best_image(text)
    if best_image_path:
        print(f"Best image path: {best_image_path}")
    else:
        print("No image found or an error occurred.")

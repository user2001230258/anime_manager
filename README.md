# Anime Manager Application

A Python-based anime management system with GUI using Tkinter and JSON storage.

## Features

- User Authentication (Admin and Regular Users)
- Image Display of Anime
- Search Functionality
- Favorites System
- Integration with Jikan API (MyAnimeList)
- JSON-based Data Storage
- Role-based Access Control

## Requirements

- Python 3.x
- Required packages:
  - tkinter
  - requests
  - Pillow (for image handling)

Install requirements using:
```bash
pip install -r requirements.txt
```

## Running the Application

Run the application using Python:
```bash
python main.py
```

## Default Login Credentials

### Admin User
- Username: admin
- Password: admin123

### Regular User
- Username: user
- Password: user123

## Features

### For All Users
- View anime list with images
- Search for anime by title
- Add/remove anime to favorites
- View favorites list
- View anime details

### Additional Admin Features
- Fetch anime data from Jikan API

## Data Storage

The application uses two JSON files for data storage:
- `users.json`: Stores user credentials, roles, and favorite lists
- `anime_data.json`: Stores anime information including images

## Using the Application

1. **Login/Register**
   - Use default credentials or register a new account

2. **Main Screen**
   - Browse anime with images
   - Use the search bar to find specific anime
   - Toggle between All Anime and Favorites view
   - Click the heart button to add/remove from favorites

3. **Admin Features**
   - Fetch new anime data from the Jikan API

## API Integration

The application integrates with the Jikan API (v4) to fetch current seasonal anime data with images. This feature is only available to admin users.

## Image Handling

The application automatically downloads and caches images from the API to provide better performance. Images are displayed in a grid layout for better visualization.

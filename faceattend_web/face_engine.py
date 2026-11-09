import face_recognition
import numpy as np


def decode_face_encoding(encoding_string):
    """Convert a stored face encoding string into a NumPy array."""
    try:
        values = np.array(
            [float(value) for value in encoding_string.split(",")],
            dtype=np.float64
        )
        if values.shape == (128,):
            return values
    except (ValueError, AttributeError, TypeError):
        pass
    return None


def load_known_faces(students):
    """Load valid face encodings from student records."""
    known_encodings = []
    known_students = []

    for student in students:
        encoding = decode_face_encoding(student.get("face_encoding"))
        if encoding is not None:
            known_encodings.append(encoding)
            known_students.append(student)

    return known_encodings, known_students


def recognize_face(image, known_encodings, known_students, threshold=0.50):
    """
    Identify faces in an RGB image.
    Returns a list of recognized students and face locations.
    """
    if image is None or len(known_encodings) == 0:
        return []

    # Convert image into a NumPy array
    image = np.asarray(image)

    # Validate image dimensions
    if image.ndim != 3 or image.shape[2] != 3:
        return []
    if image.size == 0:
        return []

    # Ensure supported image data type and memory layout
    image = np.asarray(image, dtype=np.uint8)
    image = np.ascontiguousarray(image)

    # Resize image for faster processing
    small_image = image[::4, ::4]
    small_image = np.ascontiguousarray(small_image)

    # Locate faces
    face_locations = face_recognition.face_locations(small_image, model="hog")
    if not face_locations:
        return []

    # Generate face encodings (FIX: Changed face_locations to known_face_locations)
    face_encodings = face_recognition.face_encodings(
        small_image,
        known_face_locations=face_locations, 
        num_jitters=0,
        model="small"
    )

    results = []
    for location, face_encoding in zip(face_locations, face_encodings):
        distances = face_recognition.face_distance(known_encodings, face_encoding)
        if len(distances) == 0:
            continue

        best_match_index = int(np.argmin(distances))
        best_distance = float(distances[best_match_index])

        if best_distance <= threshold:
            student = known_students[best_match_index]
            results.append({
                "student": student,
                "distance": best_distance,
                "location": location
            })

    return results
<script>
    import { onMount } from "svelte";

    const MAX_IMAGES = 8;

    let images = Array(MAX_IMAGES).fill(null);

    let mainImageIndex = 0;

    let fileInput;

    let isUploading = false;

    // Expose uploadImages function for parent component
    export function getPhotosData() {
        const photosData = images
            .filter((img) => img !== null)
            .map((img, index) => ({
                filename: img.filename,
                stored_filename: img.stored_filename,
                file_path: img.file_path,
                file_size: img.file_size,
                mime_type: img.mime_type,
                storage_type: img.storage_type,
                is_main: index === mainImageIndex,
            }));
        return photosData;
    }

    async function handleFileSelect(event) {
        const files = event.target.files;

        if (!files || files.length === 0) return;

        const emptyIndex = images.findIndex((img) => img === null);
        if (emptyIndex === -1) {
            alert("Osiągnięto maksymalną liczbę zdjęć.");
            return;
        }

        isUploading = true;

        try {
            // Upload file to server
            const formData = new FormData();
            formData.append('file', files[0]);

            const response = await fetch('/api/photos/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
                },
                body: formData
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Upload failed');
            }

            const result = await response.json();
            const fileInfo = result.file;

            // Create preview URL for display
            const previewUrl = fileInfo.file_path.startsWith('http') 
                ? fileInfo.file_path 
                : `http://localhost:5000${fileInfo.file_path}`;

            if (images.every((img) => img === null)) {
                mainImageIndex = 0;
            }

            // Store uploaded file info
            images[emptyIndex] = {
                filename: fileInfo.filename,
                stored_filename: fileInfo.stored_filename,
                file_path: fileInfo.file_path,
                file_size: fileInfo.file_size,
                mime_type: fileInfo.mime_type,
                storage_type: fileInfo.storage_type,
                url: previewUrl // For display purposes
            };

            images = [...images];

        } catch (error) {
            alert(`Błąd podczas przesyłania zdjęcia: ${error.message}`);
        } finally {
            isUploading = false;
        }

        event.target.value = "";
    }

    function removeImage(index) {
        if (index === mainImageIndex) {
            const newMainIndex = images.findIndex(
                (img, i) => i !== index && img !== null,
            );
            mainImageIndex = newMainIndex !== -1 ? newMainIndex : 0;
        }

        if (images[index] && images[index].url) {
            URL.revokeObjectURL(images[index].url);
        }
        images[index] = null;
        images = [...images];
    }

    function setAsMain(index) {
        if (images[index] !== null) {
            mainImageIndex = index;
        }
    }
    let draggedIndex = -1;

    function handleDragStart(index) {
        if (images[index] === null) return;
        draggedIndex = index;
    }

    function handleDragOver(index) {
        if (draggedIndex === -1 || draggedIndex === index) return;

        const temp = images[draggedIndex];
        images[draggedIndex] = images[index];
        images[index] = temp;

        if (mainImageIndex === draggedIndex) {
            mainImageIndex = index;
        } else if (mainImageIndex === index) {
            mainImageIndex = draggedIndex;
        }

        draggedIndex = index;

        images = [...images];
    }

    function handleDragEnd() {
        draggedIndex = -1;
    }

    onMount(() => {
        return () => {
            images.forEach((img) => {
                if (img && img.url && img.url.startsWith('blob:')) {
                    URL.revokeObjectURL(img.url);
                }
            });
        };
    });

    function uploadImages() {
        const filesToUpload = images
            .filter((img) => img !== null)
            .map((img, index) => ({
                file: img.file,
                isMain: index === mainImageIndex,
            }));

        console.log("Zdjęcia do wysłania:", filesToUpload);
    }
</script>

<div class="photo-grid">
    <h2>Zdjęcia</h2>
    <p class="instruction">
        Pierwsze zdjęcie będzie zdjęciem głównym. Przeciągaj zdjęcia na inne
        miejsca, aby zmienić ich kolejność.
    </p>

    {#if isUploading}
        <div class="upload-progress">
            <p>Przesyłanie zdjęcia...</p>
        </div>
    {/if}

    <div class="photos-container">
        {#each images as image, index}
            <div
                class="photo-slot {index === mainImageIndex
                    ? 'main-photo'
                    : ''}"
                draggable={image !== null}
                on:dragstart={() => handleDragStart(index)}
                on:dragover|preventDefault={() => handleDragOver(index)}
                on:dragend={handleDragEnd}
            >
                {#if image === null}
                    {#if index === 0}
                        <button
                            class="add-photo-btn"
                            on:click={() => fileInput.click()}
                            disabled={isUploading}
                        >
                            {isUploading ? 'Przesyłanie...' : 'Dodaj zdjęcie'}
                        </button>
                    {:else}
                        <div
                            class="empty-slot"
                            on:click={() => !isUploading && fileInput.click()}
                        >
                            <svg viewBox="0 0 24 24" class="camera-icon">
                                <path
                                    d="M9 3L7.17 5H4C2.9 5 2 5.9 2 7v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2h-3.17L15 3H9zm3 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"
                                />
                                <path
                                    d="M12 17c1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3 1.34 3 3 3z"
                                />
                            </svg>
                        </div>
                    {/if}
                {:else}
                    <div class="photo-preview">
                        <img src={image.url} alt="Podgląd zdjęcia" />
                        <div class="photo-actions">
                            {#if index !== mainImageIndex}
                                <button
                                    class="action-btn main-btn"
                                    on:click={() => setAsMain(index)}
                                    title="Ustaw jako główne"
                                >
                                    <svg viewBox="0 0 24 24">
                                        <path
                                            d="M12 17.27L18.18 21l-1.64-7.03L22 9.24l-7.19-.61L12 2 9.19 8.63 2 9.24l5.46 4.73L5.82 21z"
                                        />
                                    </svg>
                                </button>
                            {/if}
                            <button
                                class="action-btn remove-btn"
                                on:click={() => removeImage(index)}
                                title="Usuń zdjęcie"
                            >
                                <svg viewBox="0 0 24 24">
                                    <path
                                        d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
                                    />
                                </svg>
                            </button>
                        </div>
                    </div>
                {/if}
            </div>
        {/each}
    </div>

    <input
        type="file"
        bind:this={fileInput}
        on:change={handleFileSelect}
        accept="image/*"
        style="display: none;"
        disabled={isUploading}
    />

</div>

<style>
    .photo-grid {
        width: 100%;
        max-width: 900px;
        margin: 0 auto;
        padding: 20px;
    }

    h2 {
        font-size: 24px;
        margin-bottom: 8px;
        color: #333;
    }

    .instruction {
        font-size: 14px;
        color: #666;
        margin-bottom: 20px;
    }

    .upload-progress {
        background-color: #e3f2fd;
        border: 1px solid #2196f3;
        border-radius: 4px;
        padding: 12px;
        margin-bottom: 16px;
        text-align: center;
        color: #1976d2;
    }

    .photos-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
        gap: 16px;
    }

    .photo-slot {
        aspect-ratio: 4/3;
        background-color: #f2f3f5;
        border-radius: 8px;
        overflow: hidden;
        position: relative;
        cursor: pointer;
        border: 2px solid transparent;
        transition: all 0.2s ease;
    }

    .photo-slot:hover {
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }

    .main-photo {
        border-color: #0088cc;
    }

    .main-photo::before {
        content: "Zdjęcie główne";
        position: absolute;
        top: 0;
        left: 0;
        background-color: #0088cc;
        color: white;
        font-size: 12px;
        padding: 4px 8px;
        border-bottom-right-radius: 8px;
        z-index: 2;
    }

    .empty-slot {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
    }

    .camera-icon {
        width: 40px;
        height: 40px;
        fill: #8c8c8c;
    }

    .add-photo-btn {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        background-color: #fff9e6;
        border: 1px dashed #e6b800;
        color: #996600;
        font-weight: 600;
        cursor: pointer;
        transition: background-color 0.2s ease;
    }

    .add-photo-btn:hover:not(:disabled) {
        background-color: #fff5cc;
    }

    .add-photo-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .photo-preview {
        height: 100%;
        position: relative;
    }

    .photo-preview img {
        width: 100%;
        height: 100%;
        object-fit: cover;
    }

    .photo-actions {
        position: absolute;
        bottom: 0;
        right: 0;
        display: flex;
        gap: 4px;
        padding: 8px;
        background-color: rgba(0, 0, 0, 0.6);
        border-top-left-radius: 8px;
        opacity: 0;
        transition: opacity 0.2s ease;
    }

    .photo-preview:hover .photo-actions {
        opacity: 1;
    }

    .action-btn {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        border: none;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
    }

    .action-btn svg {
        width: 20px;
        height: 20px;
    }

    .main-btn {
        background-color: #0088cc;
    }

    .main-btn svg {
        fill: white;
    }

    .remove-btn {
        background-color: #ff4d4f;
    }

    .remove-btn svg {
        fill: white;
    }

    .upload-btn {
        margin-top: 20px;
        padding: 8px 16px;
        background-color: #0088cc;
        color: white;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        font-weight: 500;
    }

    .upload-btn:hover {
        background-color: #006699;
    }
</style>

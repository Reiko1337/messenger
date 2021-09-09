document.querySelector('#id_image').addEventListener('change', function () {
    const [file] = this.files;
    document.querySelector('#preview').src = URL.createObjectURL(file)
});
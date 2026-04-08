document.querySelectorAll(".rupiah").forEach(input => {

    input.addEventListener("input", function(e) {
        let angka = this.value.replace(/[^0-9]/g, "");
        
        if (angka) {
            this.value = angka.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
        } else {
            this.value = "";
        }
    });

});
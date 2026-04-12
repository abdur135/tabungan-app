document.addEventListener("DOMContentLoaded", function() {

    console.log("JS jalan");

    // FORMAT RUPIAH
    document.querySelectorAll(".rupiah").forEach(input => {
        input.addEventListener("input", function() {
            let angka = this.value.replace(/[^0-9]/g, "");

            if (angka) {
                this.value = angka.replace(/\B(?=(\d{3})+(?!\d))/g, ".");
            } else {
                this.value = "";
            }
        });
    });

    // MENU TITIK 3
    document.querySelectorAll(".menu-btn").forEach(button => {
        button.addEventListener("click", function(e) {
            e.stopPropagation();

            let dropdown = this.nextElementSibling;

            // tutup dropdown lain
            document.querySelectorAll(".dropdown").forEach(menu => {
                if (menu !== dropdown) {
                    menu.style.display = "none";
                }
            });

            // toggle
            dropdown.style.display =
                (dropdown.style.display === "block") ? "none" : "block";
        });
    });

    // klik luar = tutup
    window.addEventListener("click", function() {
        document.querySelectorAll(".dropdown").forEach(menu => {
            menu.style.display = "none";
        });
    });

});
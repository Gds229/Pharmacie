
document.getElementById('formulaire').addEventListener('submit', function(event) {
    event.preventDefault(); // Empêche le rechargement de la page
  
    var montant = document.getElementById('montant').value; // Récupère la valeur du champ de saisie
    console.log(montant); // Affiche la valeur dans la console
  
    openKkiapayWidget({amount:montant,position:"right",callback:"/success",
    data:"GDS Shop",
    theme:"green",
    sandbox:"true",
    key:"64817ef00a1311f0b26665b0670ad6cf"})
  });
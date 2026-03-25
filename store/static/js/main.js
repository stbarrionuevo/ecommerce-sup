const btn = document.querySelector("#boton-pago")
if (btn){
btn.addEventListener("click",() =>{
    if(confirm("CONFIRMAR PAGO?")){
    const urlDestino = btn.dataset.url;
    window.location.href = urlDestino
    }
    else{
        alert("Se ha cancelado el pago")
    }
})}
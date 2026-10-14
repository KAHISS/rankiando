const totalPointsValue = document.querySelector("#total-pontos-valor");

function updateTotalPoints() {
  fetch(totalPointsValue.dataset.url, {
    headers: { Accept: "application/json" },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Total de pontos indisponível (${response.status})`);
      }
      return response.json();
    })
    .then(({ total_pontos }) => {
      totalPointsValue.textContent = total_pontos;
    })
    .catch((error) => {
      totalPointsValue.setAttribute(
        "aria-label",
        "Não foi possível atualizar a pontuação total.",
      );
      console.error(error);
    });
}

window.setInterval(updateTotalPoints, 3000);

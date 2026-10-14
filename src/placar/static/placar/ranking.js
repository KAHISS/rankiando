const rankingBody = document.querySelector("#ranking-body");
const liveStatus = document.querySelector("#live-status");

function updateRanking() {
  fetch(rankingBody.dataset.rankingUrl, {
    headers: { Accept: "application/json" },
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Ranking indisponível (${response.status})`);
      }
      return response.json();
    })
    .then(({ participantes }) => {
      const rows = participantes.map(({ posicao, nome, pontos }) => {
        const row = document.createElement("tr");
        const positionCell = document.createElement("td");
        const nameCell = document.createElement("td");
        const pointsCell = document.createElement("td");

        positionCell.className = "rank-number";
        positionCell.textContent = String(posicao).padStart(2, "0");
        nameCell.className = "participant-name";
        nameCell.textContent = nome;
        pointsCell.className = "points";
        pointsCell.textContent = pontos;
        row.append(positionCell, nameCell, pointsCell);
        return row;
      });

      if (rows.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");
        row.className = "empty-row";
        cell.colSpan = 3;
        cell.textContent = "Ainda não há participantes. Seja o primeiro!";
        row.append(cell);
        rows.push(row);
      }

      rankingBody.replaceChildren(...rows);
      liveStatus.textContent = "Atualizado agora.";
    })
    .catch((error) => {
      liveStatus.textContent = "Não foi possível atualizar o ranking. Tentando novamente.";
      console.error(error);
    });
}

window.setInterval(updateRanking, 5000);

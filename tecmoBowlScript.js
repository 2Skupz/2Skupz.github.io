const teams = [
  {
    id: "chicago",
    name: "Chicago",
    nickname: "Bears",
    humanValue: "1024^400",
    defeatedValue: "xx,8A,A2,8E,82,96,86,AE,A6,9E,92,9A^1024^400^xxx,093,099,094,091,096,092,09C,09A,098,095,097"
  },
  {
    id: "cleveland",
    name: "Cleveland",
    nickname: "Browns",
    humanValue: "4^004",
    defeatedValue: "2A,xx,22,0E,02,16,06,2E,26,1E,12,1A^4^004^C87,xxx,C85,C80,B8D,C82,B8E,C88,C86,C84,C81,C83"
  },
  {
    id: "dallas",
    name: "Dallas",
    nickname: "Cowboys",
    humanValue: "256^100",
    defeatedValue: "A8,88,xx,8C,80,94,84,AC,A4,9C,90,98^256^100^D89,D81,xxx,D82,C8F,D84,D80,D8A,D88,D86,D83,D85"
  },
  {
    id: "denver",
    name: "Denver",
    nickname: "Broncos",
    humanValue: "8^008",
    defeatedValue: "2B,0B,23,xx,03,17,07,2F,27,1F,13,1B^8^008^C8C,C84,C8A,xxx,C82,C87,C83,C8D,C8B,C89,C86,C88"
  },
  {
    id: "indianapolis",
    name: "Indianapolis",
    nickname: "Colts",
    humanValue: "1^001",
    defeatedValue: "28,08,20,0C,xx,14,04,2C,24,1C,10,18^1^001^C82,B8A,C80,B8B,xxx,B8D,B89,C83,C81,B8F,B8C,B8E"
  },
  {
    id: "los-angeles",
    name: "Los Angeles",
    nickname: "Raiders",
    humanValue: "32^020",
    defeatedValue: "69,49,61,4D,41,xx,45,6D,65,5D,51,59^32^020^E86,D8E,E84,D8F,D8C,xxx,D8D,E87,E85,E83,E80,E82"
  },
  {
    id: "miami",
    name: "Miami",
    nickname: "Dolphins",
    humanValue: "2^002",
    defeatedValue: "29,09,21,0D,01,15,xx,2D,25,1D,11,19^2^002^C84,B8C,C82,B8D,B8A,B8F,xxx,C85,C83,C81,B8E,C80"
  },
  {
    id: "minnesota",
    name: "Minnesota",
    nickname: "Vikings",
    humanValue: "2048^800",
    defeatedValue: "AB,8B,A3,8F,83,97,87,xx,A7,9F,93,9B^2048^800^49C,494,49A,495,492,497,493,xxx,49B,499,496,498"
  },
  {
    id: "new-york",
    name: "New York",
    nickname: "Giants",
    humanValue: "512^200",
    defeatedValue: "A9,89,A1,8D,81,95,85,AD,xx,9D,91,99^512^200^E8A,E82,E88,E83,E80,E85,E81,E8B,xxx,E87,E84,E86"
  },
  {
    id: "san-francisco",
    name: "San Francisco",
    nickname: "49ers",
    humanValue: "128^080",
    defeatedValue: "6B,4B,63,4F,43,57,47,6F,67,xx,53,5B^128^080^498,490,496,491,39E,493,39F,499,497,xxx,492,494"
  },
  {
    id: "seattle",
    name: "Seattle",
    nickname: "Seahawks",
    humanValue: "16^010",
    defeatedValue: "68,48,60,4C,40,54,44,6C,64,5C,xx,58^16^010^D85,C8D,D83,C8E,C8B,D80,C8C,D86,D84,D82,xxx,D81"
  },
  {
    id: "washington",
    name: "Washington",
    nickname: "Redskins",
    humanValue: "64^040",
    defeatedValue: "6A,4A,62,4E,42,56,46,6E,66,5E,52,xx^64^040^097,F8F,095,090,F8D,092,F8E,098,096,094,091,xxx"
  }
];

const humanTeamOptions = document.getElementById("human-team-options");
const defeatedTeamOptions = document.getElementById("defeated-team-options");
const passwordForm = document.getElementById("password-form");
const total = document.getElementById("total");
const statusMessage = document.getElementById("statusMessage");
const resetButton = document.getElementById("resetButton");
const copyButton = document.getElementById("copyButton");

function createOptionMarkup(team, type, index) {
  const checkedTypeClass = type === "checkbox" ? "team-option is-checkbox" : "team-option";
  const inputType = type === "checkbox" ? "checkbox" : "radio";
  const inputName = type === "checkbox" ? "defeatedTeam" : "humanTeam";
  const value = type === "checkbox" ? team.defeatedValue : team.humanValue;

  return `
    <label class="${checkedTypeClass}">
      <input
        type="${inputType}"
        name="${inputName}"
        value="${value}"
        data-team-index="${index}"
      >
      <span>
        <strong>${team.name}</strong>
        <small>${team.nickname}</small>
      </span>
    </label>
  `;
}

function renderOptions() {
  humanTeamOptions.innerHTML = teams.map((team, index) => createOptionMarkup(team, "radio", index)).join("");
  defeatedTeamOptions.innerHTML = teams.map((team, index) => createOptionMarkup(team, "checkbox", index)).join("");
}

function setStatus(message) {
  statusMessage.textContent = message;
}

function setPassword(password) {
  total.textContent = password;
  copyButton.disabled = password === "------";
}

function syncDefeatedTeamAvailability() {
  const selectedHumanTeam = document.querySelector('input[name="humanTeam"]:checked');
  const selectedIndex = selectedHumanTeam ? selectedHumanTeam.dataset.teamIndex : null;
  const defeatedInputs = document.querySelectorAll('input[name="defeatedTeam"]');

  defeatedInputs.forEach((input) => {
    const option = input.closest(".team-option");
    const isSameTeam = selectedIndex !== null && input.dataset.teamIndex === selectedIndex;

    input.disabled = isSameTeam;

    if (isSameTeam) {
      input.checked = false;
      option.classList.add("is-disabled");
    } else {
      option.classList.remove("is-disabled");
    }
  });
}

function calculatePassword(selectedHumanTeam, selectedDefeatedTeams) {
  const humanTeamIndex = Number(selectedHumanTeam.dataset.teamIndex);
  const humanTeamParts = selectedHumanTeam.value.split("^");
  let def = Number(humanTeamParts[0]);
  let h = Number(humanTeamParts[1].charAt(2));
  let cgMod = Number(humanTeamParts[1].charAt(1)) + Number(humanTeamParts[1].charAt(0));
  let ab = "";
  let c = 0;
  let g = 0;

  selectedDefeatedTeams.forEach((teamInput, index) => {
    const teamParts = teamInput.value.split("^");

    if (index === 0) {
      ab = teamParts[0].split(",")[humanTeamIndex];
      const cgh = teamParts[3].split(",")[humanTeamIndex];
      c = parseInt(cgh.charAt(0), 16);
      g = parseInt(cgh.charAt(1), 16);
      h += parseInt(cgh.charAt(2), 16);
    } else {
      h += Number(teamParts[2].charAt(2));
      cgMod += Number(teamParts[2].charAt(1)) + Number(teamParts[2].charAt(0));
    }

    def += Number(teamParts[1]);
  });

  if (h >= 16) {
    h %= 16;
    c += 1;
  }

  c += cgMod;
  g += Math.floor(c / 16);
  c %= 16;

  return `${ab}${c.toString(16).toUpperCase()}${def.toString(16).toUpperCase().padStart(3, "0")}${g.toString(16).toUpperCase()}${h.toString(16).toUpperCase()}`;
}

function handleSubmit(event) {
  event.preventDefault();

  const selectedHumanTeam = document.querySelector('input[name="humanTeam"]:checked');
  const selectedDefeatedTeams = Array.from(document.querySelectorAll('input[name="defeatedTeam"]:checked'));

  if (!selectedHumanTeam) {
    setPassword("------");
    setStatus("Choose the team you are playing as first.");
    return;
  }

  if (selectedDefeatedTeams.length === 0) {
    setPassword("------");
    setStatus("Select at least one defeated team to build a password.");
    return;
  }

  const password = calculatePassword(selectedHumanTeam, selectedDefeatedTeams);
  setPassword(password);
  setStatus(`Password ready for ${teams[Number(selectedHumanTeam.dataset.teamIndex)].name}.`);
}

function handleReset() {
  passwordForm.reset();
  syncDefeatedTeamAvailability();
  setPassword("------");
  setStatus("Choose a team and at least one win to generate a password.");
}

async function handleCopy() {
  const password = total.textContent;

  if (!password || password === "------") {
    return;
  }

  try {
    await navigator.clipboard.writeText(password);
    setStatus("Password copied to the clipboard.");
  } catch (error) {
    setStatus("Copy failed. You can still highlight the password and copy it manually.");
  }
}

renderOptions();
passwordForm.addEventListener("submit", handleSubmit);
passwordForm.addEventListener("change", (event) => {
  if (event.target.name === "humanTeam") {
    syncDefeatedTeamAvailability();
  }
});
resetButton.addEventListener("click", handleReset);
copyButton.addEventListener("click", handleCopy);
syncDefeatedTeamAvailability();

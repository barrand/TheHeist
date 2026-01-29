const scenarioSelect = document.getElementById("scenarioSelect");
const rolesContainer = document.getElementById("rolesContainer");
const generateButton = document.getElementById("generateButton");
const output = document.getElementById("output");

const SCENARIOS_URL = "../data/scenarios.json";
const ROLES_URL = "../data/roles.json";
const GENERATE_URL = "http://localhost:8765/generate";

const state = {
  scenarios: [],
  roles: [],
};

const fetchJson = async (url) => {
  const response = await fetch(url);
  if (!response.ok) {
    throw new Error(`Failed to load ${url}: ${response.status}`);
  }
  return response.json();
};

const renderScenarios = () => {
  scenarioSelect.innerHTML = "";
  state.scenarios.forEach((scenario) => {
    const option = document.createElement("option");
    option.value = scenario.scenario_id;
    option.textContent = `${scenario.name} (${scenario.scenario_id})`;
    scenarioSelect.appendChild(option);
  });
};

const renderRoles = () => {
  rolesContainer.innerHTML = "";
  state.roles.forEach((role) => {
    const wrapper = document.createElement("label");
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = role.role_id;
    checkbox.checked = role.role_id === "mastermind";
    wrapper.appendChild(checkbox);
    wrapper.appendChild(document.createTextNode(role.name));
    rolesContainer.appendChild(wrapper);
  });
};

const getSelectedRoles = () =>
  Array.from(rolesContainer.querySelectorAll("input:checked")).map(
    (input) => input.value
  );

const generateChart = async () => {
  const scenarioId = scenarioSelect.value;
  const selectedRoles = getSelectedRoles();

  if (!scenarioId) {
    output.value = "Select a scenario first.";
    return;
  }

  if (selectedRoles.length === 0) {
    output.value = "Select at least one role.";
    return;
  }

  output.value = "Generating...";

  try {
    const response = await fetch(GENERATE_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        scenario_id: scenarioId,
        roles: selectedRoles,
      }),
    });

    if (!response.ok) {
      const message = await response.text();
      throw new Error(message || "Failed to generate chart.");
    }

    output.value = await response.text();
  } catch (error) {
    output.value =
      "Error generating chart. Is the server running?\n\n" + error.message;
  }
};

const init = async () => {
  try {
    const [scenariosData, rolesData] = await Promise.all([
      fetchJson(SCENARIOS_URL),
      fetchJson(ROLES_URL),
    ]);
    state.scenarios = scenariosData.scenarios || [];
    state.roles = rolesData.roles || [];
    renderScenarios();
    renderRoles();
  } catch (error) {
    output.value = `Failed to load data: ${error.message}`;
  }
};

generateButton.addEventListener("click", generateChart);

init();

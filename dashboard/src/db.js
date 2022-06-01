import { CosmosClient } from "@azure/cosmos";

const endpoint = process.env.REACT_APP_DB_ENDPOINT;
const key = process.env.REACT_APP_DB_KEY;

const client = new CosmosClient({ endpoint, key });
const database = client.database("inventory");

async function fetchTable(name) {
  const container = database.container(name);
  const { resources } = await container.items
    .query(`SELECT * from ${name}`)
    .fetchAll();

  return resources;
}

async function prepareData() {
  const warehouseData = await fetchTable("warehouse");
  const categoriesData = await fetchTable("categories");

  const categoriesDict = {};

  for (var item of categoriesData) {
    categoriesDict[item.category] = item;
  }

  const rows = warehouseData.map((item) => {
    item.allergy = categoriesDict[item.category].allergy;
    item.gasThreshold = categoriesDict[item.category].gasThreshold;

    item["Name"] = item.itemId;
    item["Sensor Data"] = item.gasValue;
    item["Weight(kg)"] = item.weight;
    item["Date"] = item.inTime;
    item["Freshness"] =
      item.gasValue < item.gasThreshold ? "Fresh" : "Not Fresh";
    item["Food Allergies Category"] = item.allergy;

    return item;
  });

  return rows;
}

export { prepareData };

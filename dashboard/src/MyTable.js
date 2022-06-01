import Table from "react-bootstrap/Table";
import { prepareData } from "./db";
import { useState, useEffect } from "react";

function MyTable() {
  const columns = [
    "Name",
    "Sensor Data",
    "Weight(kg)",
    "Date",
    "Freshness",
    "Food Allergies Category",
  ];

  const [rows, setRows] = useState([]);

  useEffect(() => {
    async function refresh() {
      const data = await prepareData();
      console.log(data);
      setRows(data);
    }
    const interval = setInterval(refresh, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Table striped bordered hover>
      <thead>
        <tr>
          {columns.map((column) => (
            <th key={column}>{column}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row) => (
          <tr key={row.itemId}>
            {columns.map((column) => (
              <td key={column}>{row[column]}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </Table>
  );
}

export default MyTable;

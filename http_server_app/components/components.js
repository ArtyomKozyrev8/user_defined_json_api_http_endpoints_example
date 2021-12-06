class CreateElements {
    static createOuterDiv(classname) {
        let div = document.createElement("div");
        div.style.display = "none";
        div.className = classname;
        return div
    }

    static createBtn(text, classname) {
        let btn = document.createElement("button");
        btn.innerText = text;
        btn.className = classname;
        return btn
    }

    static createTextArea(classname, placeholder_text) {
        let textArea = document.createElement("textarea");
        textArea.className = classname;
        textArea.setAttribute("placeholder", placeholder_text);

        return textArea
    }
}

async function asyncBtnClickWrapper (btn, asyncAction) {
    const text = btn.innerText;
    try {
        btn.innerText = "wait ...";
        btn.disabled = true;
        let r = await asyncAction;
        return r
    } finally {
        btn.innerText = text;
        btn.disabled = false;
    }
}

class Alarm {
    constructor() {
        this.outerDiv = CreateElements.createOuterDiv("alarm");
        this.innerDiv = Alarm.#createInnerDiv();
        this.btn = CreateElements.createBtn("close", "action");
    }

    static #createInnerDiv() {
        let div = document.createElement("div");
        div.innerText = "";
        return div
    }

    render() {
        this.btn.addEventListener("click", () => {
            this.outerDiv.style.display = "none";
        })
        this.outerDiv.appendChild(this.innerDiv);
        this.outerDiv.appendChild(this.btn);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
    }

    displayAlarm(message) {
        this.innerDiv.innerText = message;
        this.outerDiv.style.display = "block";
    }
}

class SendJsonReqToApiForm {
    constructor(alarm) {
        this.hideBtn = CreateElements.createBtn("SEND REQUEST TO API", "dropdown");
        this.outerDiv = CreateElements.createOuterDiv("dropdown");
        this.textArea = CreateElements.createTextArea(
            "",
            (
            "To create json body api request start typing here.\n\n" +
            "JSON message should be valid json dictionary-like object.\n\n" +
            "The object should contain key schema_name.\n\n" +
            "Value of the key should be string.\n\n" +
            "schema_name defines which rule schema to use for the request."
            )
        );
        this.btnSend = CreateElements.createBtn("send", "action");
        this.alarm = alarm;
    }

    async #sendUniversalApiRequest(json_message) {
        try {
            JSON.parse(json_message);
        } catch (e) {
            this.alarm.displayAlarm("Incorrect json message format");
            return
        }
        let url = "/api/v1/universal_api_handler";
        let resp = await fetch(
            url,
            {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: json_message,
            });
        if (resp.status === 200) {
            let data = await resp.json();
            this.alarm.displayAlarm(`Success: ${data["result"]}`);
        } else {
            let data = await resp.text();
            this.alarm.displayAlarm(`Bad request results: ${data}`);
        }
    }

    render() {
        document.getElementsByTagName("body")[0].appendChild(this.hideBtn);
        this.outerDiv.appendChild(this.textArea);
        this.outerDiv.appendChild(this.btnSend);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
        this.btnSend.addEventListener("click", async () => {
            await asyncBtnClickWrapper(this.btnSend, this.#sendUniversalApiRequest(this.textArea.value));
        });
        this.hideBtn.addEventListener("click", () => {
            if (this.outerDiv.style.display === "none") {
                this.outerDiv.style.display = "block";
            } else {
                this.outerDiv.style.display = "none";
            }
        });
    }
}

class createNewTableRowForm {
    constructor(alarm, table) {
        this.hideBtn = CreateElements.createBtn("CREATE NEW RULE SCHEMA", "dropdown");
        this.outerDiv = CreateElements.createOuterDiv("dropdown");
        this.textArea = CreateElements.createTextArea(
            "",
            (
            "To create a new rule schema start typing here.\n\n" +
            "Rule schema should be valid json dictionary-like object.\n\n" +
            "The object should contain key schema_name, value of the key should be string.\n\n"
            )
        );
        this.btnCreateNewSchema = CreateElements.createBtn("create", "action");
        this.alarm = alarm;
        this.table = table;
    }

    async #createNewRuleSchema(schema_value) {
        let url = "/api/v1/create_new_rule_schema";
        const formData  = new FormData();
        formData.append("json_schema", schema_value);
        let resp = await fetch(url, {method: 'POST', body: formData});
        let data = "";
        if (resp.status === 200) {
            data = await resp.json();
        } else {
            data = await resp.text();
            this.alarm.displayAlarm(`Failed to create a new rule schema: ${data}`);
        }
        return [resp.status, data]
    }

    render() {
        document.getElementsByTagName("body")[0].appendChild(this.hideBtn);
        this.outerDiv.appendChild(this.textArea);
        this.outerDiv.appendChild(this.btnCreateNewSchema);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
        this.btnCreateNewSchema.addEventListener("click", async () => {
            try {
                JSON.parse(this.textArea.value);
            } catch (e) {
                this.alarm.displayAlarm("Incorrect json message format");
                return
            }
            let [resp, newTableRow] =
                await asyncBtnClickWrapper(this.btnCreateNewSchema, this.#createNewRuleSchema(this.textArea.value));
            if (resp === 200) {
                this.table.appendTableBodyRow(newTableRow);
                this.table.tableRows.push(newTableRow); // append new row
                this.alarm.displayAlarm("New rule schema was successfully created");
            }
        });
        this.hideBtn.addEventListener("click", () => {
            if (this.outerDiv.style.display === "none") {
                this.outerDiv.style.display = "block";
            } else {
                this.outerDiv.style.display = "none";
            }
        });
    }
}

class searchBoxTable {
    constructor(table) {
        this.outerDiv = document.createElement("div");
        this.table = table;
        this.searchBox = this.#createInputText("search_box");
    }

    #createInputText(class_name) {
        let searchBox = document.createElement("input");
        searchBox.setAttribute("type", "text");
        searchBox.className = class_name;
        searchBox.placeholder = "Start printing here to search for rule schema name ..."
        return searchBox
    }

    render() {
        this.outerDiv.appendChild(this.searchBox);
        this.searchBox.addEventListener("keyup", (e) => {
            this.table.filterDisplayTableBody(e.target.value);
        })
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);

    }
}

class Table {
    constructor(alarm, headers) {
        this.outerDiv = document.createElement("div");
        this.alarm = alarm;
        this.tableRows = [] // probably will be used if add searchbar, etc, not used
        this.headers = headers;
        this.tableBody = document.createElement("tbody");
    }

    filterDisplayTableBody(schema_name) {
        const visRows = this.tableRows.filter(i => i["schema_name"].toLowerCase().includes(schema_name.toLowerCase()))
        this.tableBody.innerHTML = "";
        visRows.forEach(row => {
            this.appendTableBodyRow(row);
        })
    }

    static async #getDataForTable() {
        let url = "/api/v1/get_endpoint_rule_schemes";
        let resp = await fetch(url);
        if (resp.status === 200) {
            let data = await resp.json();
            return data
        } else {
            let data = await resp.text();
            return data
        }
    }

    async #deleteTableLineDb(id) {
        let url = `/api/v1/delete_endpoint_rule_scheme/${id}`;
        let resp = await fetch(url);
        if (resp.status === 200) {
            this.alarm.displayAlarm(`Successfully removed rule schema`);
            this.tableRows = this.tableRows.filter(i => i["schema_id"] != id); // update list of rows
        } else {
            let data = await resp.text();
            this.alarm.displayAlarm(`Failed to remove rule schema: ${data}`);
        }
        return resp.status
    }

    async #updateLineSchemaDb(id, schema_value) {
        let url = `/api/v1/update_rule_schema/${id}`;
        const formData  = new FormData();
        formData.append("json_schema", schema_value);
        let resp = await fetch(url, {method: 'POST', body: formData});
        let data;
        if (resp.status === 200) {
            data = await resp.json();
            data = data["result"];
            let rowToUpdate = this.tableRows.find(i => i["schema_id"] == id);
            // update list of rows element fields
            rowToUpdate["schema_id"] = data["schema_id"];
            rowToUpdate["schema_name"] = data["schema_name"];
            rowToUpdate["schema_value"] = data["schema_value"];
            this.alarm.displayAlarm(`Successfully updated rule schema`);
        } else {
            data = await resp.text();
            this.alarm.displayAlarm(`Failed to update rule schema: ${data}`);
        }
        return [resp.status, data]
    }

    appendTableBodyRow(row) {
        let body_row = document.createElement("tr");
            [row["schema_id"], row["schema_name"], row["schema_value"], "save", "delete"].forEach(
                (item, index, array) => {
                if ((index === 0) || (index === 1)) {
                    let element = document.createElement("td");
                    element.textContent = item;
                    body_row.appendChild(element);
                } else if (index === 2)  {
                    let element = document.createElement("td");
                    let textArea = CreateElements.createTextArea(
                        "in_table", "Write rule schema here");
                    textArea.setAttribute(
                        "title", "Click and start edit to change, then press save button to save changes");
                    textArea.textContent = JSON.stringify(item, undefined, 4);
                    element.appendChild(textArea);
                    body_row.appendChild(element);
                } else {
                    let element = document.createElement("td");
                    let btn = CreateElements.createBtn(item, "in_table");
                    element.appendChild(btn);
                    body_row.appendChild(element);
                }
            })
            // update btn
            body_row.children[3].children[0].addEventListener("click", async (e) => {
                let row = e.target.parentNode.parentNode;
                let id = row.children[0].innerText;
                let val = row.children[2].children[0].value; //textarea value
                try {
                    JSON.parse(val);
                } catch (e) {
                    this.alarm.displayAlarm("Incorrect json message format");
                    return
                }

                let [status, new_val] =
                    await asyncBtnClickWrapper(body_row.children[3].children[0], this.#updateLineSchemaDb(id, val));

                if (status === 200) {
                    row.children[0].innerText = new_val["schema_id"];
                    row.children[1].innerText = new_val["schema_name"];
                    row.children[2].children[0].value = JSON.stringify(new_val["schema_value"], undefined, 4);
                }
            })
            // delete btn
            body_row.children[4].children[0].addEventListener("click", async (e) => {
                let row = e.target.parentNode.parentNode;
                let id = row.children[0].innerText;
                let status = await asyncBtnClickWrapper(body_row.children[4].children[0], this.#deleteTableLineDb(id));
                if (status === 200) {
                    this.tableBody.removeChild(row);
                }
            })
            this.tableBody.appendChild(body_row);
        }

    async #createTable(rows) {
        let TheTable = document.createElement("table");

        // create table head block
        let th_row = document.createElement("tr");
        this.headers.forEach(item => {
            let element = document.createElement("th");
            element.innerHTML = item;
            th_row.appendChild(element);
        })
        let tableHead = document.createElement("thead");
        tableHead.appendChild(th_row);
        TheTable.appendChild(tableHead);

        rows.forEach(row => {
            this.appendTableBodyRow(row);
        })

        TheTable.appendChild(this.tableBody);

        return TheTable
    }

    async render() {
        const rows = await Table.#getDataForTable();
        if ( typeof this.tableRows === "string") {
            this.alarm.displayAlarm(`Failed to download schema table: ${this.tableRows}. Try to reload page`);
            return
        }
        let table = await this.#createTable(rows);
        rows.forEach(i => this.tableRows.push(i));
        this.outerDiv.appendChild(table);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
    }
}

export {Alarm, SendJsonReqToApiForm, createNewTableRowForm, Table, searchBoxTable}
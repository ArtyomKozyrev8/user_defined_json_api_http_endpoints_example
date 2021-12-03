class Alarm {
    constructor() {
        this.outerDiv = Alarm.#createOuterDiv();
        this.innerDiv = Alarm.#createInnerDiv();
        this.btn = Alarm.#createBtn();
    }

    static #createOuterDiv() {
        let div = document.createElement("div");
        div.style.display = "none";
        return div
    }

    static #createInnerDiv() {
        let div = document.createElement("div");
        div.innerText = "";
        return div
    }

    static #createBtn() {
        let btn = document.createElement("button");
        btn.innerText = "close";
        return btn
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
        this.hideBtn = SendJsonReqToApiForm.#createBtn("SEND REQUEST TO API");
        this.outerDiv = SendJsonReqToApiForm.#createOuterDiv();
        this.textArea = SendJsonReqToApiForm.#createTextArea();
        this.btnSend = SendJsonReqToApiForm.#createBtn("Send");
        this.alarm = alarm;
    }

    static #createOuterDiv() {
        let div = document.createElement("div");
        div.style.display = "none";
        return div
    }

    static #createBtn(text) {
        let btn = document.createElement("button");
        btn.innerText = text;
        return btn
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
            this.alarm.displayAlarm(`Successful request results: ${data["result"]}`);
        } else {
            let data = await resp.text();
            this.alarm.displayAlarm(`Bad request results: ${data}`);
        }
    }

    static #createTextArea() {
        let textArea = document.createElement("textarea");
        textArea.setAttribute("rows", "20");
        textArea.setAttribute("cols", "50");
        let placeholder =  (
            "To create json body for request to api start typing here.\n\n" +
            "Rule schema should be valid json dictionary-like object.\n\n" +
            "The object should contain key schema_name, value of the key should be string.\n\n" +
            "schema_name key value indicates which rule schema will be used to process the request json."
        )
        textArea.setAttribute("placeholder", placeholder);

        return textArea
    }

    render() {
        document.getElementsByTagName("body")[0].appendChild(this.hideBtn);
        this.outerDiv.appendChild(this.textArea);
        this.outerDiv.appendChild(document.createElement("br"));
        this.outerDiv.appendChild(document.createElement("br"));
        this.outerDiv.appendChild(this.btnSend);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
        this.btnSend.addEventListener("click", async () => {
            await this.#sendUniversalApiRequest(this.textArea.value);
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
        this.hideBtn = createNewTableRowForm.#createBtn("CREATE NEW RULE SCHEMA");
        this.outerDiv = createNewTableRowForm.#createOuterDiv();
        this.textArea = createNewTableRowForm.#createTextArea();
        this.btnCreateNewSchema = createNewTableRowForm.#createBtn("Create");
        this.alarm = alarm;
        this.table = table;
    }

    static #createOuterDiv() {
        let div = document.createElement("div");
        div.style.display = "none";
        return div
    }

    static #createBtn(text) {
        let btn = document.createElement("button");
        btn.innerText = text;
        return btn
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

    static #createTextArea() {
        let textArea = document.createElement("textarea");
        textArea.setAttribute("rows", "20");
        textArea.setAttribute("cols", "50");
        let placeholder =  (
            "To create a new rule schema start typing here.\n\n" +
            "Rule schema should be valid json dictionary-like object.\n\n" +
            "The object should contain key schema_name, value of the key should be string.\n\n"
        )
        textArea.setAttribute("placeholder", placeholder);

        return textArea
    }

    render() {
        document.getElementsByTagName("body")[0].appendChild(this.hideBtn);
        this.outerDiv.appendChild(this.textArea);
        this.outerDiv.appendChild(document.createElement("br"));
        this.outerDiv.appendChild(document.createElement("br"));
        this.outerDiv.appendChild(this.btnCreateNewSchema);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
        this.btnCreateNewSchema.addEventListener("click", async () => {
            try {
                JSON.parse(this.textArea.value);
            } catch (e) {
                this.alarm.displayAlarm("Incorrect json message format");
                return
            }
            let val = this.textArea.value;
            let [resp, newTableRow] = await this.#createNewRuleSchema(val);
            if (resp === 200) {
                this.table.appendTableBodyRow(newTableRow);
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

class Table {
    constructor(alarm, headers) {
        this.outerDiv = Table.#createOuterDiv();
        this.alarm = alarm;
        this.tableRows = null; // probably will be used if add searchbar, etc, not used
        this.headers = headers;
        this.tableBody = document.createElement("tbody");
    }

    static #createOuterDiv() {
        let div = document.createElement("div");
        return div
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
            data = data["result"]
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
                    let textArea = document.createElement("textarea");
                    textArea.setAttribute("rows", "20");
                    textArea.setAttribute("cols", "50");
                    textArea.setAttribute(
                        "title", "Click and start edit to change, then press save button to save changes");
                    textArea.textContent = JSON.stringify(item, undefined, 4);
                    element.appendChild(textArea);
                    body_row.appendChild(element);
                } else {
                    let element = document.createElement("td");
                    let btn = document.createElement("button")
                    btn.innerText = item;
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

                let [status, new_val] = await this.#updateLineSchemaDb(id, val);
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
                let status = await this.#deleteTableLineDb(id);
                if (status === 200) {
                    this.tableBody.removeChild(row);
                }
            })
            this.tableBody.appendChild(body_row);
        }

    async #createTable() {
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

        this.tableRows.forEach(row => {
            this.appendTableBodyRow(row);
        })

        TheTable.appendChild(this.tableBody);

        return TheTable
    }

    async render() {
        this.tableRows = await Table.#getDataForTable();
        if ( typeof this.tableRows === "string") {
            this.alarm.displayAlarm(`Failed to download schema table: ${this.tableRows}. Try to reload page`);
            return
        }
        let table = await this.#createTable();
        this.outerDiv.appendChild(table);
        document.getElementsByTagName("body")[0].appendChild(this.outerDiv);
    }
}

export {Alarm, SendJsonReqToApiForm, createNewTableRowForm, Table}
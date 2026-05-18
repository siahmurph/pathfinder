// set url  and uncomment
const url = "/api";
//const url = "http://159.89.225.137/api";

const resultsDiv = document.getElementById("results");

function validate(e) {
    const regex = /^[a-zA-Z]+$/;
    e.value = e.value
        .split("")
        .filter((char) => char.match(regex))
        .join("");
}

const formAdd = document.getElementById("formadd");
formAdd.addEventListener("submit", (e) => {
    e.preventDefault();
    const prefix = formAdd.elements["prefix"].value.toUpperCase();
    const program = formAdd.elements["seriesName"].value;
    const folderPath = formAdd.elements["folderPath"].value || "N/A";
    const locBoxes = formAdd.querySelectorAll('input[name="toWhom[]"]:checked');
    let locations = [];
    locBoxes.forEach((box) => {
        locations.push(box.value);
    });
    fetch(url + "/items", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            prefix,
            program,
            folderPath,
            locations,
        }),
    })
        .then((res) => res.json())
        .then((data) => {
            data.prefix == prefix
                ? (formAdd.reset(), alert(prefix + " added successfully!"))
                : data.message?.startsWith("UNIQUE")
                ? alert(
                      "Prefix " +
                          prefix +
                          " Already Exists. Use FIND to Edit or Delete."
                  )
                : alert("Please try again later.");
        });
});

const formFind = document.getElementById("formfind");
formFind.addEventListener("submit", (e) => {
    e.preventDefault();
    const prefix = document.getElementById("search_prefix").value.toUpperCase();
    fetch(url + "/items/" + prefix)
        .then((res) => res.json())
        .then((data) => {
            if (data && !data.message) {
                console.log(data);
                document.getElementById("searched_id").value = data.id;
                document.getElementById("searched_id_delete").value = data.id;
                document.getElementById("searched_prefix").value = data.prefix;
                document.getElementById("searched_program").value = data.series;
                document.getElementById("searched_toWeb").checked =
                    data.to_web == "YES" ? true : false;
                document.getElementById("searched_toVOS").checked =
                    data.to_vos == "YES" ? true : false;
                document.getElementById("searched_toNexio").checked =
                    data.to_nexio == "YES" ? true : false;
                document.getElementById("searched_toAffiliate").checked =
                    data.to_affiliate == "YES" ? true : false;
                document.getElementById("searched_toTMD").checked =
                    data.to_tmd == "YES" ? true : false;
                document.getElementById("searched_path").value = data.web_path;
                document.getElementById("search_prefix").value = "";
                resultsDiv.classList.remove("invisible");
            } else {
                alert("No entry found for prefix " + prefix);
                document.getElementById("search_prefix").value = "";
                resultsDiv.classList.add("invisible");
            }
        });
});

const formResult = document.getElementById("formresult");
formResult.addEventListener("submit", (e) => {
    e.preventDefault();
    const id = formResult.elements["searched_id"].value;
    const prefix = formResult.elements["searched_prefix"].value.toUpperCase();
    const program = formResult.elements["searched_program"].value;
    const folderPath = formResult.elements["searched_path"].value;
    const locBoxes = formResult.querySelectorAll(
        'input[name="updateToWhom[]"]:checked'
    );
    let locations = [];
    locBoxes.forEach((box) => {
        locations.push(box.value);
    });
    fetch(url + "/items", {
        method: "PUT",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({
            id,
            prefix,
            program,
            folderPath,
            locations,
        }),
    })
        .then((res) => res.json())
        .then((data) => {
            data.message == "good"
                ? resultsDiv.classList.add("invisible")
                : alert("Error. Please try again later.");
        });
});

const formDelete = document.getElementById("formresult_delete");
formDelete.addEventListener("submit", (e) => {
    e.preventDefault();
    const id = formDelete.elements[0].value;
    fetch(url + "/items/" + id, {
        method: "DELETE",
    })
        .then((res) => res.json())
        .then((data) => {
            if (data.message == "good") {
                document.getElementById("search_prefix").value = "";
                resultsDiv.classList.add("invisible");
            } else {
                alert("Error. Please try again.");
            }
        });
});

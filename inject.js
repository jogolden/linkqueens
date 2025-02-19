// Inject me into Linkedin queens browser page

async function clickSquare(n) {
    let node = document.querySelector("#queens-grid > div:nth-child(" + (n + 1) + ")");
    node.dispatchEvent(new Event("mousedown", { bubbles: true, cancelable: true }));
    node.dispatchEvent(new Event("mouseup", { bubbles: true, cancelable: true }));

    // Allow the DOM/framework a moment to process the event
    await new Promise((resolve) => setTimeout(resolve, 25));
}

function squareState(n) {
    let node = document.querySelector("#queens-grid > div:nth-child(" + (n + 1) + ")");
    let content = node.querySelector("div.cell-content");

    // check empty
    if (content.children.length == 0) {
        return 0;
    }

    // check first child class list
    let cl = content.children[0].classList[1];

    if (cl == "cell-input--cross") {
        return 1;
    } else if (cl == "cell-input--queen") {
        return 2;
    }

    return -1;
}

function squareColor(n) {
    let node = document.querySelector("#queens-grid > div:nth-child(" + (n + 1) + ")");

    // find the color class
    for (let i = 0; i < node.classList.length; i++) {
        const cls = node.classList[i];
        if (cls.startsWith("cell-color-")) {
            const colorStr = cls.substring("cell-color-".length);
            const colorInt = parseInt(colorStr, 10);
            return Number.isNaN(colorInt) ? -1 : colorInt;
        }
    }

    return -1;
}

async function placeQueen(n) {
    let state = squareState(n);

    if (state == 0) {
        // empty square, needs 2
        await clickSquare(n);
        await clickSquare(n);
    } else if (state == 1) {
        // x square, needs 1
        await clickSquare(n);
    } else {
        // already a queen??
    }
}

async function loadState(state) {
    const rows = state.length;
    const cols = state[0].length;

    for (let i = 0; i < rows; i++) {
        for (let j = 0; j < cols; j++) {
            if (state[i][j] === 1) {
                let index = i * cols + j;

                await placeQueen(index);
            }
        }
    }
}

function getRegions() {
    let grid = document.querySelector("#queens-grid");
    let styles = window.getComputedStyle(grid);
    let rows = parseInt(styles.getPropertyValue("--rows"), 10);
    let cols = parseInt(styles.getPropertyValue("--cols"), 10);

    let result = [];

    for (let i = 0; i < rows; i++) {
        let rowArray = [];
        for (let j = 0; j < cols; j++) {
            let idx = i * cols + j;
            rowArray.push(squareColor(idx));
        }

        result.push(rowArray);
    }

    return result;
}

async function postBoard(board) {
    try {
        const response = await fetch("http://127.0.0.1:8000/solve", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(board)
        });

        if (!response.ok) {
            throw new Error(`network response was not ok: ${response.statusText}`);
        }

        const data = await response.json();
        return data;
    } catch (error) {
        console.error("error posting board:", error);
        throw error;
    }
}

async function getResult() {
    try {
        const response = await fetch("http://127.0.0.1:8000/result", { mode: 'cors' });
        if (!response.ok) {
            throw new Error(`network response was not ok: ${response.statusText}`);
        }
        const data = await response.json();
        return data;
    } catch (error) {
        console.error("error fetching data:", error);
        throw error;
    }
}

// Start game button
const btn = document.getElementsByClassName("launch-footer__btn--start");
if (btn != null && btn.length > 0) {
    btn[0].click();

    // Allow the DOM/framework a moment to process the event
    await new Promise((resolve) => setTimeout(resolve, 50));
}

// Solve the queens puzzle!
let regions = getRegions();
let s1 = await postBoard(regions);
if (s1["message"] === "started") {
    while (true) {
        let s2 = await getResult();
        if (s2["status"] === "completed") {
            await loadState(s2["result"]);
            break;
        } else if (s2["status"] === "not started" || s2["status"] === "pending") {
            continue;
        }
    }
} else {
    console.log("error: already running solver?");
}

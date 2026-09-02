const fs = require('fs');

async function run() {
    try {
        const response = await fetch('https://workplace-pulse-app-996129350542.us-central1.run.app/api/scenarios/seed', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ scenario_id: 'hardware_lifecycle' })
        });
        const payload = await response.json();
        
        console.log("saas_metrics length:", payload.saas_metrics ? payload.saas_metrics.length : 'undefined/null');
        console.log("hardware_metrics length:", payload.hardware_metrics ? payload.hardware_metrics.length : 'undefined/null');
        
        if (payload.saas_metrics && payload.saas_metrics.length > 0) {
            console.log("WOULD RENDER SAAS");
        } else if (payload.hardware_metrics && payload.hardware_metrics.length > 0) {
            console.log("WOULD RENDER HARDWARE");
        } else if (payload.itsm_metrics && payload.itsm_metrics.length > 0) {
            console.log("WOULD RENDER ITSM");
        } else {
            console.log("WOULD RENDER NOTHING");
        }
    } catch (e) {
        console.error(e);
    }
}
run();

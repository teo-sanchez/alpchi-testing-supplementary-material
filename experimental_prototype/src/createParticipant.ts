// DATA STORAGE
import { dataStore } from '@marcellejs/core';


export async function createParticipant(pid: number) {
    try {
        // Connect to the datastore
        const store = dataStore('http://localhost:3030');

        // Sergice for participant IDs
        const pidService = store.service("pid");

        // Create services for testSet and user-interaction
        store.service("testSet-{pid}".replace("{pid}", pid.toString()));
        store.service("user-interaction-{pid}".replace("{pid}", pid.toString()));

        // Check if participant with given PID already exists
        const result = await pidService.find({
            query: {
                pid: pid,
                $sort: { updatedAt: -1 }, // Sort by updatedAt in descending order
                $limit: 1
            }
        }) as { data: unknown[] };

        // If participant does not exist, create it
        if (result.data.length === 0) {
            pidService.create({pid: pid});
            console.log("Participant ID n°{pid} has been succesfully created.".replace("{pid}", pid.toString()));
        } else {
            console.log("Participant ID n°{pid} has already been used on this computer.".replace("{pid}", pid.toString()));
            alert("Participant ID n°{pid} has already been used on this computer. Data might have already been collected for this participant.".replace("{pid}", pid.toString()));
        }
    } catch (error) {
        console.error(error);
        alert("An error occured while creating the participant. Please contact the experiment administrator.");
    }
}
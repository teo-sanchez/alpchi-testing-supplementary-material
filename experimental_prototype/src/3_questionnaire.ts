import { Experiment } from './components';
import { ExperimentPageOptions } from "./components/experiment";
import { button } from '@marcellejs/core';

const instructions_options : ExperimentPageOptions = {
    name: "Questionnaire",
    instructions: "You finished the test set creation phase. Please now click on the button bellow to access the final questionnaire.",
    navigationMode: 'automatic',
    navigationButtons: 'none',
    ratioRightSidebar: 0.45,
    ratioLeftSidebar: 0.45
}

const questionnaireButton = button("To the questionnaire");
questionnaireButton.title = "";

questionnaireButton.$click.subscribe(() => {
    const questionnaireUrl = "https://www.soscisurvey.de/ML_Auditing"
    window.open(questionnaireUrl, '_blank');
})

export function setup(exp : Experiment) {
    exp.page(instructions_options)
        .use(questionnaireButton)
}
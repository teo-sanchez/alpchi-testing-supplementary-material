import '@marcellejs/core/dist/marcelle.css';
// Import layout
import { experiment } from './components';
import { ExperimentOptions } from './components/experiment';

import { createParticipant } from './createParticipant';
import { setup as setupInstructions } from './1_instructions';
import { setup as setupTestSet } from './2_test_set_creation';
import { setup as setupQuestionnaire } from './3_questionnaire';

const exp_options: ExperimentOptions = {
  title: 'Research experiment',
  author: '',
  freeNavigation: true,
};

const exp = experiment(exp_options);

// Retrieve PID from command line arguments
const pid = (import.meta as any).env.VITE_PID;

// Setup model

createParticipant(pid);
setupInstructions(exp);
setupTestSet(exp);
setupQuestionnaire(exp);

exp.show();

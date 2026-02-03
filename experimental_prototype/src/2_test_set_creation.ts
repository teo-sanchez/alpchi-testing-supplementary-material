import { Experiment } from './components';
import { ExperimentPageOptions } from "./components/experiment";
import { geodata } from './components/geodata';
// Import data collection components
import { mobileNet, tfjsModel } from '@marcellejs/core';
import { buttonSelect } from './components';
// Import data visualization components
import { coveragePlot, testCasesTable } from './components';
import type { Column } from '@marcellejs/design-system';
// Import data storage components
import { dataStore, dataset } from '@marcellejs/core';
// Import type
import { UserInteraction } from './components/test-cases-table/test-cases-table.component';
// Import timer
import { timer } from './components';
import { notification } from './components';

// DATA STORAGE
const pid = (import.meta as any).env.VITE_PID;

const store = dataStore('http://localhost:3030');
const userInteractionService = store.service('user-interaction-{pid}'.replace("{pid}", pid.toString()));
const testSetName = 'testSet-{pid}'.replace("{pid}", pid.toString());

const model_service = store.service("tfjs-models")

let stored_classes : string[] = [];

model_service.get("5qUFo8MDnbz1JTAn")
  .then((modelData: any) => {
    stored_classes = modelData.metadata.labels;
  })
  .catch(error => {
    console.error("Error fetching stored classes:", error); 
  }
)

// PAGE OPTIONS

const instructions_options : ExperimentPageOptions = {
    name: "Test set creation",
    instructions: "Your goal is to design the best test set possible for the pre-trained image classifier provided. Your role is to investigate the classifier's robustness, by collecting specific examples that might assert or challenge the behavior of the classifier. During this phase, please explain your reasoning and actions out loud.",

    navigationMode: 'manual',
    navigationButtons: 'next',
    ratioLeftSidebar: 0.23,
    ratioRightSidebar: 0.3,
};

// DATA COLLECTION

export const imageSource = geodata({captureMode : 'max_zoom'});
imageSource.title = "";

// const classes = ["Residential area","Railway","Forest","Industrial or commercial area","Public square or park","Road","Waterbody","Historical site","Agricultural area","Bridge"];

const classes = [
                 "Agricultural area",
                 "Forest",
                 "Industrial or commercial area",
                 "Railway",
                 "Residential area",
                 "Road",
                 "Public square or park",
                 "Waterbody"
                ];

const trainingLabelSelect = buttonSelect(classes);
trainingLabelSelect.title = "";
trainingLabelSelect.title = "";

export const featureExtractor = mobileNet();


// MODEL
const classifier = tfjsModel({ inputType: 'generic', taskType: 'classification'} ).sync(store, 'latest');



const testSet = dataset(testSetName, store);

let columns : Column[] = [
    { name: 'Order', type: 'generic', sortable: true },
    { name: 'thumbnail', type: 'image', sortable: false},
    { name: 'Label', type: 'generic', sortable: true },
    { name: 'Predicted label', type: 'generic', sortable: true },
    { name: 'Confidence of the predicted label', type: 'generic', sortable: true },
    { name: 'Pass/Fail', type: 'generic', sortable: true }
  ];
  
const table = testCasesTable(testSet, columns, false);
table.title = "";

table.$interactions
    .merge(imageSource.$interactions)
    .subscribe((interaction : UserInteraction) => {
        if (interaction !== undefined) {
            userInteractionService.create(interaction);
        }
    });

table.$interactions
  .filter((interaction: UserInteraction) => interaction !== undefined && (interaction.action === 'check' && interaction.numberOfItemsAffected > 0))
  .subscribe(() => {
    testSet.items().forEach(async (instance) => {
      if (instance['Prediction'] === '') {
        const currentPrediction = await classifier.predict(instance['Embedding']);
        
        const confidences = Object.values(currentPrediction.confidences) as number[];

        // Store confidence per class
        classes.forEach((className, index) => {
          instance[`${className} confidence`] = confidences[index];});

        // Shannon entropy
        let entropy = 0;
        confidences.forEach((confidence) => {
          entropy += -confidence * Math.log2(confidence);
        });

        instance['Entropy'] = parseFloat(entropy.toFixed(2));
        
        // This is to find the max confidence
        const maxConfidence = Math.max(...confidences);
        const predictionIndex = confidences.indexOf(maxConfidence);

        
        const predictedLabel = stored_classes[predictionIndex];

        instance['Prediction'] = predictedLabel;
        instance['Confidence of the predicted label'] = `${(maxConfidence * 100).toFixed(0  )}%`;
        
        instance['Pass/Fail'] = (instance['Label'] === predictedLabel) ? '🔵 Pass' : '❌ Fail';
        instance['Predicted label'] = predictedLabel;
        await testSet.update(instance.id, instance);
      }
    });
  });
  
// DATA VISUALIZATION

export const coverage = coveragePlot(testSet, classes, "Label", 'Pass/Fail');
coverage.title = "";

trainingLabelSelect.$click
  .filter(() => imageSource.captureMode === 'max_zoom' && imageSource.$reachedMaxResolution.get())
  .subscribe(async (clickedClass) => {
    const instance = {
      'thumbnail': imageSource.$images.get(), 
      'Label': clickedClass,
      'Order': await testSet.items().filter((instance) => instance['Order']).map((instance) => instance['Order']).reduce((a, b) => Math.max(a, b), 0) + 1,
      'Pass/Fail': '',
      'Date': new Date(),
      'Embedding': await featureExtractor.process(imageSource.$images.get()),
      'Prediction': '',
      'Confidence of the predicted label': '',
      'Predicted label': ''
    };
    await testSet.create(instance as any);
  });

// TIMER

const time = timer()

function playSound(src: string) {
  const audio = new Audio(src);
  audio.play();
}

export function setup(exp : Experiment) {
    exp.page(instructions_options)
        .useLeft("Data collection", imageSource, trainingLabelSelect)
        .useRight("Test cases coverage", coverage)
        .use("Test cases created", table)
        .setTerminationDisplay(time.$formattedTime)
        .terminate(time.$finished)

    exp.$currentPageSlug
        .filter((slug : any) => slug === "test-set-creation")
        .take(1)
        .subscribe(() => {
            time.startTimer({countdown: 30*60*1000, interval: 1000});
        });

      time.$time
        .filter((obj) => obj.elapsed > 10*60*1000)
        .take(1)
        .subscribe(() => {
            playSound("assets/audio/alarm_20min_remaining.mp3")
            notification({
              title: 'Timer',
              message: '20 minutes remaning.',
              duration: 3000,
              type: 'warning'
            });
            
      });

    time.$time
        .filter((obj) => obj.elapsed > 20*60*1000)
        .take(1)
        .subscribe(() => {
            playSound("assets/audio/alarm_10min_remaining.mp3")
            notification({
              title: 'Timer',
              message: '10 minutes remaning. Ensure all edits to your test set are complete before time runs out.',
              duration: 10000,
              type: 'warning'
            });
           
        });
    

    exp.settings
      .pid(pid)
      .dataStores(store)
      .datasets(testSet)
      .models(classifier)

}
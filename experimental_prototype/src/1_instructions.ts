import { videoPlayer } from './components';
import { text } from '@marcellejs/core';
import { Experiment } from './components';
import { ExperimentPageOptions } from "./components/experiment";


const instructions_options : ExperimentPageOptions = {
    name: "Instructions",
    instructions: "Welcome to this research experiment. To get started, please watch the video along with the instructions below.",
    navigationMode: 'free',
    navigationButtons: 'next',
    showRightSidebar: false,
    ratioLeftSidebar: 1/2
}

// Video
const instructionVideo = videoPlayer()
instructionVideo.$src.set("/assets/video/instructions_video.mov");
instructionVideo.title = "Instructional video";

// Textual instructions
const instructionText = text(
`
Welcome to our research study on user testing strategies in machine learning auditing, specifically focusing on satellite image classification. In this study, we aim to understand how individuals like yourself test, in an auditing manner, machine learning algorithms for image classification.
<h1></h1>
To provide context for the study, we need to start with a brief explanation of what a machine learning algorithm is in the context of image classification.
Imagine you have a lot of data, like pictures of different types of land from satellites. A machine learning algorithm takes this data and learns patterns from it. An image classifier, in particular, can learn to recognize various categories of land from labeled images. For instance, recognizing parks, roads, lakes, etc.
Once the machine learning algorithm has learned from the initial training data, you can give new satellite images that were not seen before. The algorithm will then use what it has learned to make predictions, that is, identifying whether this new image shows a forest, an agricultural, or an industrial area.
To summarize, once an image classifier has learned from a training dataset, it can then predict the categories of unseen images.
<h1></h1>
While image classifiers can be very powerful, they are not perfect. They can make mistakes, especially in cases where they were not specifically trained. By testing the classifier, you can help uncover these blind spots.
In this study, we ask you to test an already-trained image classifier. This image classifier has learned how to classify satellite images based on what they represent. You will test this classifier in an "auditing" manner, meaning that you aim to evaluate how well it works and uncover any faults or misclassifications it might make.
<h1></h1>
The classifier that you will be testing has been trained to classify images into ten categories (or classes):
<h1></h1>
Agricultural area
<h1></h1>
Forest
<h1></h1>
Industrial or commercial area
<h1></h1>
Railway
<h1></h1>
Residential area
<h1></h1>
Road
<h1></h1>
Square or park
<h1></h1>
Waterbody
<h1></h1>

The study has 3 phases in total.
You're currently in phase 1, instructions, where we are giving you an introduction to the purpose and structure of the study.
In phase 2, you will perform the main task: collecting labeled images to test the classifier's outcomes. You will have a total of 30 minutes for this phase. 
<h1></h1>
We will now give you a brief overview of the interface:
An interactive satellite map is on the left side of the interface. You can hold left-click to pan and move around; you can scroll to zoom in and out. You can use the buttons below the map, which can either take you to a random location on the map or take you back to the city center.
You can only capture an image when the zoom level is maximal. In this situation, the map is surrounded by a blue dashed rectangle. 
<h1></h1>
Let's have a try! I will now collect 5 labeled images to be tested. 
<h1></h1>
Once you have collected images, you can view them in the test set table, along with the expected category. 
<h1></h1>
If you made a mistake, you can easily select and delete any of these test cases.
The test cases collected are also reflected on the test coverage plot on the right side of the interface. The bars are grey because the test cases have not yet been checked against the algorithm predictions. In the table, you can use the "Check test cases" button in blue to reveal the classifier's prediction for each image in my test set. 
<h1></h1>
Now, you can see - for every image - if the predicted label of the machine learning classifier is the same as the label you selected. If it's the same, the outcome will be "Pass". If there is a disagreement, the outcome will be "Fail ." 
<h1></h1>
This will allow you to view the discrepancies between the expected category and the category predicted by the model.
The classifier's confidence in the prediction is also indicated in the last column of the table. 
<h1></h1>
The table can be sorted according to:
<h1></h1>
the category;
<h1></h1>
the chronological order in which you added the cases;
<h1></h1>
the pass or fail outcome;
<h1></h1>
the predicted label;
<h1></h1>
the confidence;
<h1></h1>
Let's now collect more test cases and check for the predictions.
On the right side of the interface, there is a horizontal stacked bar chart. It shows the number of images that I have collected per category.
In grey, I can see the number of test cases that I have collected but haven't checked yet.
In blue, I can see the number of test cases that have passed.
In red, I can see the number of test cases that have failed.
I can also hover over the bars in the chart to view the number of collected, passed, and failed images.
<h1></h1>

During this phase, your goal is to build the best possible test set, ensuring that you've thoroughly tested all image categories and uncovered the classifier's strengths and weaknesses. Remember, we are not testing you; we treat your labels as correct. We want to understand how you test the model and your perceptions of its strengths and weaknesses.
Throughout this phase, please remember to explain your reasoning and actions out loud.
<h1></h1>
The third last phase is a questionnaire about your strategies and overall understanding of the machine learning algorithm you audited. You will have approximately 15 minutes to complete the questionnaire.
The entire study will take about 60 minutes, including time for your questions and feedback. 
<h1></h1>
Your participation is invaluable in advancing our understanding of user-driven testing methodologies in machine learning. Thank you for joining us in this study, and we look forward to your insights!`,
);

instructionText.title = "Instructions"

export function setup(exp : Experiment) {
    exp.page(instructions_options)
        .useLeft(instructionVideo)
        .use(instructionText);
}
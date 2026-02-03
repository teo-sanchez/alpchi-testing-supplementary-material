# 1. Introduction

Welcome to our research study on user testing strategies in machine learning auditing. In this study, we aim to understand how individuals like you, with or without expertise, can review a machine learning algorithm. You will engage with an image classifier, which is an algorithm that can assign categories to images. This image classifier was trained on satellite images of Munich, Germany, and its surroundings. Your goal is to test this machine learning algorithm to investigate its robustness under various inputs.

# 2. Background: What is machine learning?

To provide context for the study, we need to briefly explain what image classification is in the context of machine learning.
An image classifier is an algorithm that can predict a category from an image. Nowadays, machine learning techniques are used to build image classifiers. A machine learning algorithm can process data gathered in a training set and learn patterns from them. In our case, the training set is composed of satellite images labeled with different types of land.

After this training set is collected, the image classifier processes the data statistically to learn the association between satellite images, the inputs, and their categories, the outputs. Once trained, the machine learning algorithm can predict categories, such as parks, roads, and lakes, from images it has not seen before.

Machine learning developers usually gather those unseen images into a distinct set called a test set, on which they compute a performance score.

# 3. Goal

In this study, YOU will be in charge of creating a test set for an already-trained image classifier, to investigate its robustness under various inputs and reveal the classifier's strengths and weaknesses. After the study, we will use your test set to estimate a performance score of the pre-trained classifier.

The classifier that you will be testing has been trained to classify images into eight categories:

- Agricultural area
- Forest
- Industrial or commercial area
- Railway
- Residential area
- Road
- Square or park
- Waterbody

# 4. Procedure

The study has 3 phases in total.

You are currently in phase 1, instructions, which explain the goal and structure of the study.

In phase 2, you will perform the main task: test the classifier's outcomes using labeled images of Munich and its surroundings.
You will have a total of 30 minutes to refine the best test set possible by collecting test cases that assert or challenge the behavior of the pre-trained image classifier. Throughout this phase, you will be asked to explain your reasoning and actions out loud.

The third last phase is a questionnaire about your strategies and overall understanding of the machine learning algorithm you tested. It takes approximately 15 minutes to complete the questionnaire.

The entire study will take about 60 minutes, including time for any questions you might have.

# 5. Interface overview

We will now give you an overview of the interface in phase 2.

## 5.1 Interactive satellite map

An interactive satellite map is on the left side of the interface. You can hold left-click to pan and move around, and scroll to zoom in and out. You can use the buttons below the map, which can either take you to a random location in the surroundings of Munich, Germany, or take you back to the city center.
You can only capture an image when the zoom level is maximal. In this situation, the map is surrounded by a blue dashed rectangle.

Let's have a try! I will now collect 5 labeled images to test the pre-trained image classifier.

## 5.2 Test set table

Once you have collected images, you can view them in the test set table in the center of the screen, along with the category you chose.

The leftmost column, named "Order," is the order in which the labeled image was collected. The second column shows a thumbnail image of the image considered. The third column, named "Label", is the label you expect to be predicted by the classifier.

You can easily select and delete any of these test cases if you make a mistake or realize the example is not suitable for your test set.

The number of examples collected per category is also shown on a horizontal bar chart graph on the right side of the interface. The bars are grey because the examples have not yet been checked against the algorithm predictions.

In the table, you can use the "Check test cases" button in blue to reveal the classifier's prediction for each image in the test set.
You can check the collected examples at any time.

After you click on "Check test cases," the image classifier predicts a label for every image collected, shown in the fourth column named "Predicted label."
The fifth column, named "Confidence of the predicted label," indicates a percentage of certainty about the prediction made by the classifier.

Finally, last column shows if the test case you created, which correspond to a row in the table, passes or fails.

The test case passes if the predicted label of the classifier is the same as the label you selected. The test case fails if there is a disagreement between the label you chose and the label predicted.

This column enables you to easily reflect on the discrepancies between the category you expected and the category predicted by the pre-trained image classifier.

The test cases in the table can be sorted according to each column, either in ascending or decreasing order, by simply clicking on the small arrow next to the column title.

## 5.2 Bar chart

After you check your test set, which you can do at any time and as many times as you wish, the changes are reflected in the horizontal bar chart on the rightmost side of the interface.

This chart is cumulative and shows the number of examples per category collected:

- In grey, you can see the number of examples collected but haven't been checked yet;
- In blue, you can see the number of examples that have passed, which are examples correctly predicted by the pre-trained classifier;
- In red, you can see the number of examples that have failed, which are examples incorrectly predicted by the pre-trained classifier.
  You can also hover over the bars in the chart to view the exact number of unchecked, passed, and failed images per category.

# 6. Conclusion

In this study, your goal is to design the best test set possible for the pre-trained image classifier provided. Your role is to investigate the classifier's robustness under various inputs.

To do so, you have to collect test cases, which are specific examples that might assert or challenge the behavior of the pre-trained classifier.
Remember, we are not testing your annotations but treating your labels as correct.
After the study, we will use your test set to estimate a performance score of the pre-trained classifier.

Thank you for joining us in this study, and we look forward to your insights!

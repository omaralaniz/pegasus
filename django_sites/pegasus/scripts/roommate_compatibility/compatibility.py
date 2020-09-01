import os
import logging
import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.metrics.pairwise import euclidean_distances
from joblib import dump, load


def load_model(filename):
    return load(filename)


def save_model(model, filename):
    dump(model, filename, )


class CompatibilityClassifier(object):
    def __init__(self):
        self.default_input_csv = 'student_compat.csv'

        # Silence TensorFlow warnings
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

    def build_score_data(self, filename=None):
        if not filename:
            filename = self.default_input_csv

        logging.info("Building scoring dataset from '%s'..." % filename)
        self.scores = pd.read_csv(filename)

        # Drop irrelevant columns
        self.scores = self.scores.drop(columns=['Timestamp', 'Hobbies', 'Unnamed: 14'], axis=1)

        # One-hot encoding for Major
        self.scores = pd.get_dummies(scores, columns=['Major'])
        self.scores = self.scores.values

    def generate_pca(self):
        # PCA for purposes of visualization in 2D only - should be removed for 'production'
        logging.info("Running PCA...")
        pca = PCA(n_components=2, random_state=123, svd_solver='auto')
        self.df_pca = pd.DataFrame(pca.fit_transform(self.scores))
        logging.info("PCA head: %s" % self.df_pca.head())

    def train_kmeans(self):
        def input_function():
            return tf.train.limit_epochs(tf.convert_to_tensor(self.scores, dtype=tf.float32), num_epochs=1)

        num_clusters = 5
        num_iterations = 10
        kmeans = tf.contrib.factorization.KMeansClustering(num_clusters=num_clusters, use_mini_batch=False)

        logging.info("Starting training...")
        for _ in range(num_iterations):
            kmeans.train(input_function)
            cluster_centers = kmeans.cluster_centers()

        logging.info("Mapping input points to their respective clusters...")
        cluster_indices = list(kmeans.predict_cluster_index(input_function))
        all_points = []
        for i, point in enumerate(self.scores):
            cluster_index = cluster_indices[i]
            all_points.append(point)
            center = cluster_centers[cluster_index]
            logging.debug("Point: %s is in cluster %s centered at %s." % (point, cluster_index, center))

        # cluster_indices is an array of size num_points that contains the cluster number assignment for each record
        logging.info("Clusters: %s" % cluster_indices)

        # all_points is an array of size num_points, holding all coordinates for each point
        logging.info("Coordinates of each point: %s" % all_points)

        # cluster_centers is an array of size k, that holds coordinates for the center of each cluster
        logging.info("Cluster center coordinates: %s" % cluster_centers)
        self.cluster_centers = cluster_centers


class CompatibilityLabeler(object):
    def __init__(self, classifier_filename):
        try:
            logging.info("Loading model from '%s'..." % classifier_filename)
            self.classifier = load_model(classifier_filename)
        except:
            logging.error("Could not load model from '%s'." % classifier_filename)

    def predict_cluster(self, student):
        # Simple method to classify a single student, using euclidian distance to
        # cluster centers new_student has same coordinates as student at index 11,
        # so should be cluster to cluster 4
        dists = euclidean_distances(self.classifier.cluster_centers, student, squared=True)
        logging.info("Euclidian Distances: %s" % dists)

        closest_cluster = np.argmin(dists)
        logging.info("Predicted cluster: %s" % closest_cluster)
        return closest_cluster


if __name__ == "__main__":
    classifier_filename = 'classifier.pkl'

    # Configure log
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

    # Generate and train a classifier
    def test_train():
        classifier = CompatibilityClassifier()
        classifier.build_score_data()
        classifier.train_kmeans()
        save_model(classifier, classifier_filename)

    # Use classifier to test against a student
    def test_label():
        new_student = [[3, 8, 10, 7, 3, 7, 3, 5, 9, 5, 8, 0, 0, 0, 0, 1, 0]]
        labeler = CompatibilityLabeler(classifier_filename)
        if labeler:
            labeler.predict_cluster(new_student)


    # test_train()
    test_label()

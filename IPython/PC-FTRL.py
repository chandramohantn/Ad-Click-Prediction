"""
Author: CHANDRAMOHAN T N
File: PC-FTRL.py 
"""

import math
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import sys
from sklearn import metrics

def Get_data(i_f):
	f = open(i_f, 'r')
	data = []
	while 1:
		line = f.readline()
		line = line[0:-1]
		if len(line) > 0:
			items = map(int, line.split(','))
			data.append(items)
		else:
			f.close()
			break
	return data

def Get_labels(i_f):
	f = open(i_f, 'r')
	labels = []
	while 1:
		line = f.readline()
		line = line[0:-1]
		if len(line) > 0:
			labels.append(int(line))
		else:
			f.close
			break
	return labels

def sigmoid(x):
	return 1.0 / (1.0 + np.exp(-x))

def log_likelihood(x, y, w):
	p = sigmoid(np.dot(x, w))
	loss = -y * np.log(p) - (1 - y) * np.log(1 - p)
	return loss.mean()

def gradient(x, y, w):
	p = sigmoid(np.dot(x, w))
	grad = np.dot(np.transpose(x), (p - y))
	return grad.reshape(w.shape)

def plot(a, b, c, x, l, n):
	plt.plot(x, a, 'r', label='AUC Loss')
	plt.plot(x, b, 'g', label='Log Loss')
	plt.plot(x, c, 'b', label='Sq Error')
	plt.title(l)
	plt.legend(loc='upper right')
	plt.ylabel('Loss')
	if n == 1:
		plt.xlabel('Iteration')
		plt.savefig('PC-FTRL Test Loss.png')
	else:
		plt.xlabel('Lambda')
		plt.savefig('PC-FTRL Performance.png')
	plt.close()

class PC_FTRL(object):

	def __init__(self, x, y):
		self.x = np.concatenate((np.ones((len(x), 1)), np.array(x)), axis=1)
		self.y = np.array(y).reshape(len(y), 1)
		self.w = np.zeros((self.x.shape[1], 1))
		self.z = np.zeros((self.x.shape[1], 1))
		self.gr = np.zeros((self.x.shape[1], 1))

	def train_ogd(self, lmbda1, lmbda2, alpha, beta, idx):
		x = self.x[idx * 1: (idx+1) * 1]
		y = self.y[idx * 1: (idx+1) * 1]
		g = gradient(x, y, self.w)
		lr = np.sqrt(self.gr + (g **2) - np.sqrt(self.gr))) / alpha
		self.z = self.z + g - lr * self.w
		self.gr = self.gr + (g ** 2)
		temp = np.zeros((self.w.shape[0], 1))
		indx = ((np.absolute(self.z) > lmbda1).nonzero())[0]
		for k in indx:
			temp[k] = -(self.z[k] - np.sign(self.z[k]) * lmbda1) / ((beta + np.sqrt(self.gr)) / alpha + lmbda2)
		self.w = temp
		return self.w

	def update_weights(self, w):
		self.w = w

	def save_model(self):
		np.savez_compressed('Model_pc-ftrl', w=self.w, z=self.z)

	def predict(self, x):
		labels = [0 for i in xrange(len(x))]
		p = sigmoid(np.dot(x, self.w))
		for i in xrange(len(x)):
			if p[i] > 0.5:
				labels[i] = 1
		return p, labels

	def evaluate(self, y_pred, y_true, test_x):
		fpr, tpr, thresholds = metrics.roc_curve(y_true, y_pred)
		auc = metrics.auc(fpr, tpr)
		auc_loss = 1 - auc
		log_loss = log_likelihood(test_x, y_true, self.w)
		sq_error = np.sum((y_pred - y_true)**2) / y_pred.shape[0]
		return auc_loss, log_loss, sq_error

def main():
	i_f = '../Data/books/Train_x.csv'
	train_x = Get_data(i_f)
	i_f = '../Data/books/Test_x.csv'
	test_x = Get_data(i_f)
	test_x = np.concatenate((np.ones((len(test_x), 1)), np.array(test_x)), axis=1)
	i_f = '../Data/books/Train_y.csv'
	train_y = Get_labels(i_f)
	i_f = '../Data/books/Test_y.csv'
	test_y = Get_labels(i_f)
	test_y = np.reshape(test_y, (test_x.shape[0], 1))

	max_iter = 15000
	alpha = 0.02
	beta = 1.0
	lmbda = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
	prev_auc_loss = sys.maxint
	te_auc_loss = []
	te_log_loss = []
	te_sq_error = []
	for l in lmbda:
		print('Lambda2: ' + str(l))
		pc_ftrl_reg = PC_FTRL(train_x, train_y)
		tr_auc_loss = []
		tr_log_loss = []
		tr_sq_error = []
		for i in range(max_iter):
			idx = np.random.randint(len(train_x))
			w = pc_ftrl_reg.train_ogd(1, l, alpha, beta, idx)
			pc_ftrl_reg.update_weights(w)
			if (i+1) % 500 == 0:
				y_prob, y_pred = pc_ftrl_reg.predict(test_x)
				a, b, c = pc_ftrl_reg.evaluate(y_prob, test_y, test_x)
				tr_auc_loss.append(a)
				tr_log_loss.append(b)
				tr_sq_error.append(c)
		y_prob, y_pred = pc_ftrl_reg.predict(test_x)
		a, b, c = pc_ftrl_reg.evaluate(y_prob, test_y, test_x)
		te_auc_loss.append(a)
		te_log_loss.append(b)
		te_sq_error.append(c)
		if a < prev_auc_loss:
			prev_auc_loss = a
			best_l = l
			pc_ftrl_reg.save_model()
			r = [k for k in range(len(tr_auc_loss))]
			plot(tr_auc_loss, tr_log_loss, tr_sq_error, r, 'PC-FTRL Test_loss, lambda2= ' + str(best_l), 1)
	plot(te_auc_loss, te_log_loss, te_sq_error, lmbda, 'PC-FTRL Performance', 2)

if __name__ == '__main__':
	main()

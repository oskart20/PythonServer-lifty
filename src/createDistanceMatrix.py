#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
from __future__ import print_function
import requests

import Json


def create_data(locations):
	"""Creates the data."""
	data = {}
	data['API_key'] = Json.get_config_api_key()
	string = ''
	temp = []
	for x in locations:
		string = ''
		for y in x:
			string = string + str(y) + "+"
		string = string[:-1]
		temp.append(string)
	data['addresses'] = temp
	return data


def create_distance_matrix(data):
	addresses = data["addresses"]
	API_key = data["API_key"]
	# Distance Matrix API only accepts 100 elements per request, so get rows in multiple requests.
	max_elements = 100
	num_addresses = len(addresses)  # 16 in this example.
	# Maximum number of rows that can be computed per request (6 in this example).
	max_rows = max_elements // num_addresses
	# num_addresses = q * max_rows + r (q = 2 and r = 4 in this example).
	q, r = divmod(num_addresses, max_rows)
	dest_addresses = addresses
	distance_matrix = []
	time_matrix = []
	# Send q requests, returning max_rows rows per request.
	for i in range(q):
		origin_addresses = addresses[i * max_rows: (i + 1) * max_rows]
		response = send_request(origin_addresses, dest_addresses, API_key)
		distance_matrix += build_distance_matrix(response)
		time_matrix += build_time_matrix(response)
	# Get the remaining remaining r rows, if necessary.
	if r > 0:
		origin_addresses = addresses[q * max_rows: q * max_rows + r]
		response = send_request(origin_addresses, dest_addresses, API_key)
		distance_matrix += build_distance_matrix(response)
		time_matrix += build_time_matrix(response)
	return distance_matrix, time_matrix


def send_request(origin_addresses, dest_addresses, API_key):
	""" Build and send request for the given origin and destination addresses."""
	def build_address_str(addresses):
		# Build a pipe-separated string of addresses
		address_str = ''
		for i in range(len(addresses) - 1):
			address_str += addresses[i] + '|'
		address_str += addresses[-1]
		return address_str
	request = 'https://maps.googleapis.com/maps/api/distancematrix/json?units=metric'
	origin_address_str = build_address_str(origin_addresses)
	dest_address_str = build_address_str(dest_addresses)
	request += '&origins=' + origin_address_str + '&destinations=' + dest_address_str + '&key=' + API_key
	json_result = requests.get(request)
	response = json_result.json()
	return response


def build_distance_matrix(response):
	distance_matrix = []
	# print(response)
	print(response['status'])
	for row in response['rows']:
		row_list = [row['elements'][j]['distance']['value'] for j in range(len(row['elements']))]
		distance_matrix.append(row_list)
	return distance_matrix

def build_time_matrix(response):
	time_matrix = []
	# print(response)
	print(response['status'])
	for row in response['rows']:
		row_list_time = [row['elements'][j]['duration']['value'] for j in range(len(row['elements']))]
		time_matrix.append(row_list_time)
	return time_matrix

def main(locations):
	# Create the data.
	data = create_data(locations)
	distance_matrix, time_matrix = create_distance_matrix(data)
	print(distance_matrix)
	print(time_matrix)
	return distance_matrix, time_matrix
class Node(object):
	def __init__(self, data=None, next_node=None):
		self.data = data
		self.next_node = next_node

	def get_data(self):
		return self.data

	def get_next(self):
		return self.next_node

	def set_next(self, new_next):
		self.next_node = new_next

class LinkedList(object):
	def __init__(self, head=None):
		self.head = head

	def insert(self, data):
		new_node = Node(data)
		new_node.set_next(self.head)
		self.head = new_node

	def size(self):
		current = self.head
		count = 0
		while current:
			count += 1
			current = current.get_next()
		return count

	def search(self, data):
		current = self.head
		found = False
		while current and found is False:
			if current.get_data() == data:
				found = True
			else:
				current = current.get_next()
		if current is None:
			raise ValueError('Data not in list')
		return current

	def delete(self, data=None):
		"""Deletes the node with specified data from the list. 
		If no data is specified, deletes the last element in the list"""
		current = self.head
		previous = None
		found = False
		while current and found is False:
			if data is not None and current.get_data() == data:
				found = True
			elif data is None and current.get_next() is None:
				found = True
			else:
				previous = current
				current = current.get_next()
		if current is None:
			raise ValueError('Data not in list')
		else:
			previous.set_next(current.get_next())

	def get_list(self):
		current = self.head
		unlinked = []
		while current:
			unlinked.append(current.data)
			current = current.get_next()
		return unlinked

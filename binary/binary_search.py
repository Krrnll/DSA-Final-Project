from typing import Optional

from .binary_tree import BinaryTree, TreeNode


class BinarySearchTree(BinaryTree):
    """Binary Search Tree implementation"""
    def insert(self, value: int) -> bool:
        """Insert value into BST following BST property"""
        if self.root is None:
            self.root = TreeNode(value)
            return True
        return self._insert_recursive(self.root, value)
    
    def _insert_recursive(self, node: TreeNode, value: int) -> bool:
        if value < node.value:
            if node.left is None:
                node.left = TreeNode(value)
                return True
            return self._insert_recursive(node.left, value)
        elif value > node.value:
            if node.right is None:
                node.right = TreeNode(value)
                return True
            return self._insert_recursive(node.right, value)
        else:
            # Value already exists
            return False
    
    def delete(self, value: int) -> bool:
        """Delete a node from BST maintaining BST property"""
        # Check if node exists before deletion
        if not self.search(value):
            return False
        self.root = self._delete_recursive(self.root, value)
        return True
    
    def _delete_recursive(self, node: Optional[TreeNode], value: int) -> Optional[TreeNode]:
        if node is None:
            return None
        
        if value < node.value:
            node.left = self._delete_recursive(node.left, value)
        elif value > node.value:
            node.right = self._delete_recursive(node.right, value)
        else:
            # Node to delete found
            if node.left is None:
                return node.right
            elif node.right is None:
                return node.left
            else:
                # Node has two children - find inorder successor
                min_node = self._find_min(node.right)
                node.value = min_node.value
                node.right = self._delete_recursive(node.right, min_node.value)
        return node
    
    def _find_min(self, node: TreeNode) -> TreeNode:
        """Find minimum value node"""
        while node.left:
            node = node.left
        return node
    
    def search(self, value: int) -> bool:
        """Search for a value in BST"""
        return self._search_recursive(self.root, value)
    
    def _search_recursive(self, node: Optional[TreeNode], value: int) -> bool:
        if node is None:
            return False
        if node.value == value:
            return True
        if value < node.value:
            return self._search_recursive(node.left, value)
        else:
            return self._search_recursive(node.right, value)
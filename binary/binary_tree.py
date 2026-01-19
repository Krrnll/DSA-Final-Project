from collections import deque
from typing import Optional


class TreeNode:
    """Node representation used by both BinaryTree and BST."""

    def __init__(self, value: int):
        self.value = value
        self.left: Optional["TreeNode"] = None
        self.right: Optional["TreeNode"] = None
        # Coordinates used by the UI visualizer
        self.x = 0
        self.y = 0


class BinaryTree:
    """Basic Binary Tree implementation"""

    def __init__(self):
        self.root: Optional[TreeNode] = None

    def insert(self, value: int) -> bool:
        """Insert value into binary tree (level-order insertion)"""
        if self.root is None:
            self.root = TreeNode(value)
            return True

        # Level-order insertion using deque for better performance
        queue = deque([self.root])
        while queue:
            node = queue.popleft()

            if node.left is None:
                node.left = TreeNode(value)
                return True
            elif node.right is None:
                node.right = TreeNode(value)
                return True
            else:
                queue.append(node.left)
                queue.append(node.right)
        return False

    def delete(self, value: int) -> bool:
        """Delete a node from binary tree"""
        if self.root is None:
            return False

        # Find the node and the deepest node
        node_to_delete: Optional[TreeNode] = None
        deepest_node: Optional[TreeNode] = None
        parent_of_deepest: Optional[TreeNode] = None

        # Find node to delete using deque for better performance
        queue = deque([(self.root, None)])
        while queue:
            node, parent = queue.popleft()
            if node.value == value:
                node_to_delete = node
            if node.left or node.right:
                if node.left:
                    queue.append((node.left, node))
                if node.right:
                    queue.append((node.right, node))
            else:
                deepest_node = node
                parent_of_deepest = parent

        if node_to_delete is None:
            return False

        # Replace node_to_delete with deepest_node
        if deepest_node and node_to_delete != deepest_node:
            node_to_delete.value = deepest_node.value
            if parent_of_deepest and parent_of_deepest.left == deepest_node:
                parent_of_deepest.left = None
            elif parent_of_deepest:
                parent_of_deepest.right = None
        elif node_to_delete == self.root:
            self.root = None

        return True

    def search(self, value: int) -> bool:
        """Search for a value in binary tree"""
        return self._search_recursive(self.root, value)

    def _search_recursive(self, node: Optional[TreeNode], value: int) -> bool:
        if node is None:
            return False
        if node.value == value:
            return True
        return self._search_recursive(node.left, value) or self._search_recursive(node.right)

    def get_height(self, node: Optional[TreeNode] = None) -> int:
        """Get height of the tree"""
        if node is None:
            node = self.root
        if node is None:
            return 0
        return 1 + max(self.get_height(node.left), self.get_height(node.right))

    def inorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Inorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.extend(self.inorder_traversal(node.left))
            result.append(node.value)
            result.extend(self.inorder_traversal(node.right))
        return result

    def preorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Preorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.append(node.value)
            result.extend(self.preorder_traversal(node.left))
            result.extend(self.preorder_traversal(node.right))
        return result

    def postorder_traversal(self, node: Optional[TreeNode] = None) -> list:
        """Postorder traversal"""
        if node is None:
            node = self.root
        result = []
        if node:
            result.extend(self.postorder_traversal(node.left))
            result.extend(self.postorder_traversal(node.right))
            result.append(node.value)
        return result
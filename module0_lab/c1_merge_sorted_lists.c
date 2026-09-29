/*
 * Prerequisite Assessment — C Problem 1: Merge Two Sorted Lists
 *
 * Merge two sorted linked lists and return it as a sorted list.
 * The list should be made by splicing together the nodes of the
 * first two lists.
 *
 * Constraints:
 *   - The number of nodes in both lists is in the range [0, 50]
 *   - -100 <= Node.val <= 100
 *   - Both list1 and list2 are sorted in non-decreasing order
 *
 * Instructions:
 *   - Implement the mergeTwoLists function below
 *   - Do NOT modify the struct definition or main()
 *   - Compile: gcc -o c1 c1_merge_sorted_lists.c
 *   - Run:     ./c1 < input.txt
 */
//ok
#include <stdio.h>
#include <stdlib.h>

struct ListNode {
    int val;
    struct ListNode *next;
};

/* ──────────────────────────────────────────────
   TODO: Implement this function
   ────────────────────────────────────────────── */
struct ListNode* mergeTwoLists(struct ListNode* list1, struct ListNode* list2) {
    /* Your implementation here */
    struct ListNode head;
    head.next = NULL;
    struct ListNode* cur = &head;
    while (list1 && list2 ) {
        if (list1->val <= list2->val) {
            cur->next = list1;
            list1 = list1->next;
        } else {
            cur->next = list2;
            list2 = list2->next;
        }
        cur = cur->next;
        
    }
    if (list1 != NULL) {
        cur->next = list1;
    } else {
        cur->next = list2;
    }
    return head.next;
    return NULL;
}

/* ── Harness (do NOT modify below) ────────────── */
struct ListNode* buildList(int* arr, int n) {
    if (n == 0) return NULL;
    struct ListNode* head = malloc(sizeof(struct ListNode));
    head->val = arr[0];
    head->next = NULL;
    struct ListNode* cur = head;
    for (int i = 1; i < n; i++) {
        cur->next = malloc(sizeof(struct ListNode));
        cur->next->val = arr[i];
        cur->next->next = NULL;
        cur = cur->next;
    }
    return head;
}

void printList(struct ListNode* head) {
    printf("[");
    while (head) {
        printf("%d", head->val);
        if (head->next) printf(",");
        head = head->next;
    }
    printf("]\n");
}

void freeList(struct ListNode* head) {
    while (head) {
        struct ListNode* tmp = head;
        head = head->next;
        free(tmp);
    }
}

int main() {
    int n1, n2;
    /* Read: n1 elements of list1, then n2 elements of list2 */
    scanf("%d", &n1);
    int a1[50];
    for (int i = 0; i < n1; i++) scanf("%d", &a1[i]);
    scanf("%d", &n2);
    int a2[50];
    for (int i = 0; i < n2; i++) scanf("%d", &a2[i]);

    struct ListNode* l1 = buildList(a1, n1);
    struct ListNode* l2 = buildList(a2, n2);
    struct ListNode* merged = mergeTwoLists(l1, l2);
    printList(merged);
    freeList(merged);
    return 0;
}

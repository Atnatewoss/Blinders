; ---------------------------------------------------------------------------
; Step 2: Symbolic Verification Laws (Universal Logic)
; ---------------------------------------------------------------------------

; Permission Proof: Direct Fact
(= (permission_proof $role $perm)
   (match &self (permission $role $perm) True))

; Permission Proof: Recursive Inheritance
(= (permission_proof $role $perm)
   (match &self (isA $role $parent) (permission_proof $parent $perm)))

; Inheritance Trace
(= (inherits $child $ancestor) (== $child $ancestor))
(= (inherits $child $ancestor)
   (match &self (isA $child $parent) (inherits $parent $ancestor)))

; Context Check
(= (context_check $key $value $law)
   (match &self (context $key $value) True))

; Simple Budget Check (Rule L4 Variant)
(= (budget_check $team $cost $law)
   (match &self (team_budget $team $balance) 
      (match &self (check_action_cost $action $cost) 
         (>= $balance $cost))))

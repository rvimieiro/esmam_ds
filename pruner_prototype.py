import copy
from rule import Rule


class Pruner:

    def __init__(self, dataset, terms_mgr, sg_comparison):
        self._terms_mgr = terms_mgr
        self._dataset = dataset
        self.current_rule = None
        self._comparison = sg_comparison

    def prune(self, rule: Rule, verbose=False) -> Rule:
        """Prune rule's antecedent while its quality measure does not decrease
        or rule's length is greater than one condition.
        At each iteration all conditions are tested for removal, being chosen 
        the one which promotes maximum overall quality improvement.
        """
        self.current_rule = rule
        if verbose:
            print()
            print(50*'*')
            print()
            print("Received for pruning:", self.current_rule.antecedent)
            print("\nOriginal fitness:", self.current_rule.fitness)
            print()

        pruned_rule = Rule(self._dataset, self._comparison)

        if len(self.current_rule.antecedent) == 1:
            if verbose:
                print("Cannot be pruned: one antecedent only.")
                print()
        else:
            pruning_iteration = 1
            if verbose:
                print("\tInitializing pruning procedure\n")

            while len(self.current_rule.antecedent) > 1:
                if verbose:
                    print("\tIteration {}, pruning".format(pruning_iteration),
                          self.current_rule.antecedent, '\n')
                temp = (self.current_rule.fitness, None)
                for attr in self.current_rule.antecedent:
                    pruned_rule.antecedent = self.current_rule.antecedent.copy()
                    pruned_rule.antecedent.pop(attr, None)
                    pruned_rule.set_cases(
                        self._terms_mgr.get_cases(
                            pruned_rule.antecedent
                        )
                    )
                    pruned_rule.set_fitness()
                    if verbose:
                        print("\t\t>> Fitness without '{}':".format(attr),
                              pruned_rule.fitness)
                    if pruned_rule.fitness >= temp[0]:
                        temp = (pruned_rule.fitness, attr)
                        if verbose:
                            print(
                                "\n\t\t\tPruned rule maintains or improves quality.")
                            print(
                                "\n\t\t\tSetting '{}' attribute for removal".format(attr))
                    else:
                        if verbose:
                            print("\n\t\t\tPruned rule decreases quality.")
                    if verbose:
                        print()

                if temp[1] is None:
                    if verbose:
                        print("\tPruning does not improve overall quality.\n")
                    break
                if verbose:
                    print(
                        "\t\t(!) Deleting {} from pruned rule's antecedent.".format(temp[1]))
                    print()
                del self.current_rule.antecedent[temp[1]]

                pruning_iteration += 1

            # Setting final rule's fitness
            self.current_rule.set_cases(
                self._terms_mgr.get_cases(self.current_rule.antecedent)
            )
            self.current_rule.set_fitness()

            if verbose:
                print("\tEnd of pruning procedure, returning rule:\n")
                print("\t\t@ Antecedent:", self.current_rule.antecedent)
                print()
                print("\t\t@ Fitness:", self.current_rule.fitness)
                input()

        return self.current_rule

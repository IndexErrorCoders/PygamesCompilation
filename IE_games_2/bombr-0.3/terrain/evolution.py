"""Implements a framework for doing evolutionary tests"""

import random
import copy

import loggable


class DNAError(Exception):
    """An error occurred applying a DNA action"""


class BadOrganism(DNAError):
    """The organism created is not valid"""


class CannotMutate(DNAError):
    """A strand cannot mutate in the way attempted"""


class mutator(object):
    """A decorator to flag a method as a mutator function"""

    def __init__(self, probability):
        """Initialise the decorator"""
        self.probability = probability

    def __call__(self, f):
        """Create the decorator"""
        def wrapped(*args):
            return f(*args)
        wrapped.isMutator = True
        wrapped.probability = self.probability
        return wrapped


class DNA(object):
    """Represents the base DNA"""

    def __init__(self, chromosomes):
        """Initialise the DNA"""
        self.chromosomes = chromosomes
        self.mutators = self.getMutators()

    def getMutators(self):
        """Return the mutators for this DNA"""
        result = []
        total_probability = 0.0
        for fn in self.__class__.__dict__.values():
            if hasattr(fn, 'isMutator'):
                result.append((total_probability + fn.probability, fn))
                total_probability += fn.probability
        #
        self.total_mutation_probability = total_probability
        #
        return result

    @classmethod
    def getNew(cls):
        """Return a new strand of DNA - override this to create new copies"""
        return cls(cls.getRandomInitialChromosomes())

    def getCopy(self):
        """Return a copy of this DNA"""
        return self.__class__(copy.deepcopy(self.chromosomes))

    @classmethod
    def getRandomInitialChromosomes(cls):
        """Return some random chromosomes to start with"""
        return None

    def getMutation(self, *args, **kw):
        """Return a mutation"""
        new = self
        for p, fn in self.mutators:
            if random.random() < p:
                new = fn(new, *args, **kw)
        return new

    def makeOrganism(self, *args, **kw):
        """Return an organism created from this DNA"""
        return None


class Controller(loggable.Loggable):
    """A controller for controlling the evolutionary process"""

    def __init__(self):
        """Initialise the controller"""
        self.addLogger()
        self.dna = None
        self.pool = []

    def setDNA(self, dna):
        """Set the DNA to use"""
        self.dna = dna

    def createInitialPool(self, number):
        """Create an initial pool of DNA items"""
        if not self.dna:
            raise ValueError('No DNA set for the controller')
        for _ in range(number):
            self.pool.append(self.dna.getNew())

    def getPool(self):
        """Return the pool of items"""
        return self.pool

    def appendToPool(self, strand):
        """Add a strand to the pool"""
        self.pool.append(strand)

    def extendPool(self, strands):
        """Add strands to the pool"""
        self.pool.extend(strands)

    def rankPool(self, *args, **kw):
        """Rank and sort the pool so that the top item is at the top"""
        items = []
        for item in self.pool:
            item.organism = item.makeOrganism(*args, **kw)
            item.score = self.scoreFitness(item.organism)
            items.append((item.score, item))
        items.sort()
        items.reverse()
        self.pool[:] = [item[1] for item in items]

    def scoreFitness(self, item):
        """Score the fitness of the item"""
        return 1.0

    def performTournament(self, size, iterations, *args, **kw):
        """Perform a number of iterations of a tournament of a certain size

        Breaks the pool into a set of sub-pools of size "size". Then each
        sub-pool is ranked and has the bottom half overwritten by new
        mutations of the top half.

        """
        if size > len(self.pool):
            raise ValueError('Tournament size (%d) is greater than the pool size (%d)' % (size, len(self.pool)))
        if len(self.pool) % size != 0:
            raise ValueError('Tournament size (%d) is not a multiple of pool size (%d)' % (size, len(self.pool)))
        if size % 2 != 0:
            raise ValueError('Tournament size (%d) is not even' % size)
        #
        # Create sub pools
        sub_pools = []
        random.shuffle(self.pool)
        num_sub_pools = len(self.pool) / size
        for _ in range(num_sub_pools):
            #
            # Create new sub-pool
            sub_pool = self.getCopy()
            sub_pool.setDNA(self.dna)
            sub_pools.append(sub_pool)
            for _ in range(size):
                sub_pool.appendToPool(self.pool.pop())
        #
        # Now perform iterations
        self.reportProgress(0.0, None)
        for iteration in range(iterations):
            self.log.info('Starting iteration %d' % iteration)
            self.pool[:] = []
            for sub_pool in sub_pools:
                sub_pool.performIteration(size, *args, **kw)
                self.extendPool(sub_pool.getPool())
            #
            self.pool.sort(lambda a, b: cmp(a.score, b.score))
            if not self.reportProgress(100.0 * iteration / iterations, self.pool[-1].organism):
                break
        #
        # And rank overall
        self.rankPool(*args, **kw)

    def getCopy(self):
        """Return a copy of ourself"""
        return self.__class__()

    def performIteration(self, target_pool_size, *args, **kw):
        """Perform a tournament iteration"""
        if len(self.getPool()) == 0:
            self.log.warn('Pool is exhausted - no more valid organisms')
            return
        #
        # Make sure pool is ranked
        self.rankPool(*args, **kw)
        #
        half = max(1, len(self.pool) / 2)
        #
        # Use top half of pool to create new second half
        self.pool = self.pool[:half]
        for idx in range(target_pool_size - half):
            start = random.choice(self.pool[:half])
            try:
                new = start.getMutation(*args, **kw)
            except CannotMutate:
                self.log.debug('Item cannot mutate')
            else:
                self.appendToPool(new)
        #
        # Rank
        self.rankPool(*args, **kw)
        #
        self.log.info('Iteration done: %s' % ([item.score for item in self.pool], ))

    def reportProgress(self, percent, best):
        """Report progress if you can"""
        return True
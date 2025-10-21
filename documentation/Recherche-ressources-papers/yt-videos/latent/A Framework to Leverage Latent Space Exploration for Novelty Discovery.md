https://www.youtube.com/watch?v=MAC544dQ9no

Hey everybody. So, this is a super
0:02
interesting research paper that caught
0:04
my eye very specifically because like I
0:07
would be I'm not going to say that like
0:09
at least one of these authors have come
0:11
across my work definitively, but I would
0:13
be like there's a lot of coincidences is
0:16
how I would frame that overall, right?
0:18
And then so uh like that's good overall.
0:20
And this research paper is called large
0:22
language models as innovators, a
0:23
framework to leverage latent space
0:26
exploration for novelty discovery. Uh
0:29
and then so this research paper deals
The Framework
0:32
very specifically with LLM models and
0:34
the latent space whereas like all of my
0:36
research I mean like a majority of my
0:39
research is around like swarm algorithms
0:42
and uh latent space exploration in this
0:46
manner but let's dive into this right so
0:49
this is their framework and then so
0:51
essentially how this framework breaks
0:53
down is uh you take two ideas right idea
0:57
A and idea B and then you vector them.
0:59
So vectorized idea A vector idea B you
1:03
combine those two vector two vectors via
1:07
ideiation uh and then essentially you
1:10
get uh a result like a probabilistic
1:12
result that uh is comes out of that uh
1:15
and then that blended result and you can
1:17
blend you can utilize different reward
1:19
mechanisms for that blending process and
1:22
like uh you can blend over multiple
1:25
generations right like I'll show you an
1:26
example we blend like 25 generations out
1:29
Right. Uh and then so uh it's possible
1:32
to to and then that's essentially just
1:34
what this uh process is overall.
1:37
And then what this process operates off
1:40
of is the latent space of the models,
1:43
right? And then the latent space uh this
1:45
process essentially operates off of the
1:47
latent space being almost like a
1:49
physical object having an it's being an
1:52
enclosed space with physics um inside of
1:55
that space. Right? So it's it is a
1:57
physics-based object in that that
1:59
particular sense like 1 million%.
2:01
And then but so uh diving deeper into
2:05
this like uh so their method is is pure
2:08
LM model and I'll showcase that to you
2:10
but like uh I want to showcase I've been
2:13
working on and and hypothesizing around
2:16
this particular method now for like like
2:18
a couple of years basically right uh I I
2:21
equate it out in different ways. So to
2:24
me the latent space is essentially like
2:25
a magic box and then so you can drop a
2:28
problem into the magic box and then so
2:31
the problem would be a vector right so
2:33
we drop the problem vector into the
2:35
magic box uh and then we have we'll call
2:38
them solution variables and then
2:39
solution variables would be uh things
2:42
that we think would lead towards a
2:43
solution but we're not 1 million% sure
2:46
but we want to create connections
2:48
between the problem vector and the
2:50
solution variables and then essentially
2:52
we oper operate and we control the box
2:55
in that manner, right? And then we
2:56
essentially we drop an agent in there
2:59
and then the agent uh it should be able
3:01
to figure out and then if there's enough
3:04
solution variables that connect to the
3:06
problem vector, the agent should be able
3:08
to figure out what the solution is
3:09
within the problem space like within
3:11
that latent space of the problem. Uh and
3:13
then so I've gone over kind of like a
3:16
few different models uh and built them
3:18
out like within this like here overall
3:20
I'll just highlight them. Right? So
3:21
you've got this uh swarm neural network
3:23
image diffusion v2 like which is 100%
3:26
related to this a swarm poker agent
3:28
100%. Uh API call diffusion with swarm
3:31
neural networks uh coin 2.5 2.05b
3:34
5B uh swarm function caller. Uh this one
3:39
the SNN image generator uh API call
3:42
swarm caller. Um yeah, so all like
3:45
essentially like seven of these are all
3:47
related to this concept, right? And then
3:49
I also have um this notebook here which
Notebook
3:51
I made here we go uh like a few months
3:54
ago or like back in February is when I
3:56
made this particular one. Uh but so uh
3:59
essentially what this notebook is is so
4:01
this is the target image, right? So this
4:03
is the original image
4:06
and then we get our end output here. So
4:08
this end output isn't actually an image.
4:11
This is swarm algorithms recreating this
4:14
image within the latent space. Right? So
4:16
I drop the image as the problem vector
4:19
and then I give it enough solution
4:21
variables in order to recreate the image
4:23
of the cat. Uh and then we can do the
4:26
same thing with like uh sentences and
4:28
and and text here. So like you know here
4:30
we've got like just a noisy sentence
4:32
that we we deconstruct uh and then I've
4:34
got it like I start training the model
4:36
on this instance and and then through
4:38
here. But so there's a lot of different
4:40
things that you can do uh with this this
4:43
uh uh latent space right this solution
4:46
space it doesn't have like I'm showing
4:48
it can be images text video whatever you
4:50
would want to put into latent space
4:52
right it would it would be um
4:54
significant amount of compute to put
4:56
video into it but then so let's break
4:58
this concept down into um an applicable
Code
5:01
code specifically for this paper so this
5:04
paper breaks down and it utilizes well
5:07
sorry uh it utilizes is uh LM models uh
5:11
in this instance and it talks about LM
5:13
models for the laten space. So we'll
5:14
focus on that. Although I do want to
5:17
point out one thing here that we will
5:19
focus on as well within this uh because
5:21
it's majority of my research within this
5:24
but so uh looking ahead several avenues
5:27
for future research emerge. Developing
5:29
more sophisticated latent space
5:30
exploration strategies such as
5:32
swarm-based optimization algorithms will
5:34
be crucial to include increase the
5:36
efficiency of idea generation and
5:38
improve flexibility. They called out
5:40
right there very specifically, right?
5:42
So, uh let's go ahead and go over here.
5:44
Uh and then we've got our latent space
5:47
ideation with advanced swarm clean
5:49
optimization. So this Google Collab
5:51
notebook implements a powerful latenc
5:54
ideation framework that combines these
5:55
strengths of modern language models and
5:57
swarm intelligence. It allows users to
6:00
generate novel highquality ideas by
6:03
navigating and manipulating embedding
6:05
spaces using a customuilt swarm queen
6:08
optimization mechanism. So what this
6:11
notebook does, it encodes ideas into
6:13
embeddings utilizing sentence
6:16
transformers, explores latent space via
6:18
a swarm of intelligent agents guided by
6:20
essential swarm queen, interpolates and
6:23
it mutates the concepts in the vector
6:25
space to spark new innovations and then
6:28
it decodes ideas back to human language,
6:30
scores and ranks those ideas. Uh and
6:33
then so real world use cases of this
6:35
like so the first example of this is and
6:37
and first use case is we combine uh like
6:40
a smart water water bottle uh that
6:43
tracks hydration with a solar powered
6:46
portable charger to discover a product
6:48
that is a solar powered smart water
6:50
bottle that tracks hyd hydration and
6:52
purifies water utilizing sunlight. Uh
6:55
and then so I'll demonstrate and and
6:57
showcase that here for you. Right? So
6:59
here's uh all the code. I vectorize the
7:01
two concepts uh and then I give it like
7:04
a a bunch of potential solutions in this
7:06
instance right and then so in this first
7:08
instance I'm giving it a bunch of
7:10
potential solutions rather than giving
7:12
it like an LLM model or anything like
7:14
that in order to uh like uh do anything
7:18
you know further with that and then so
7:20
again we have our ideas idea number one
7:22
and idea number two idea number one
7:24
being a smart water bottle that tracks
7:25
hydration and reminds you to drink and
7:27
then idea number two being a portable
7:29
solar charger for electronic devices.
7:32
And then it essentially searches through
7:34
the latent space to come up with a new
7:36
product idea, which is a water bottle
7:38
that generates its own power from the
7:40
sun to run smart features like tracking
7:43
intake and powering a purification
7:45
system. And then so this idea was
7:47
identified because its conceptual vector
7:49
was closest to the average of the smart
7:52
water bottle and the solar charge
7:54
vectors. And then so that's very
7:56
specifically and simplistically how it
7:58
was able to come up with the solution in
8:00
that particular instance. Uh and then so
8:03
uh as mentioned and as previewed they
8:05
mentioned that the best way to do this
8:07
and to take this forward would probably
8:08
be to do a solution like combining LM
8:11
models with uh swarm op like swarm
8:14
algorithms in this particular instance
8:16
right and then so that's what we do uh
8:18
in this particular instance in this
8:20
second notebook here uh is we combine it
8:22
with my swarm queen optimization and
8:24
then I I utilize a gamma 2b a gamma 1B
8:28
uh model in this instance gamma 2 1B uh
8:32
sorry GMA Gamma 2B uh in this instance
8:36
uh to train the model and to be the LM
8:39
model in this instance and then so what
8:42
we do is we first of all we score we
8:44
create and we score five ideas right and
8:47
then so uh the swarm invol like so we
8:50
have our five ideas and then we create
8:52
them into vectors code them into vectors
8:54
and then uh ideulate based off of those
8:56
vectors and then so like the concepts
8:58
get kind of crazy cuz they're they get
9:00
into like kind of stories and then the
9:03
model is uh creating these on its own,
9:06
right? So it creates concepts and I also
9:08
cut it off really quickly as like 70
9:10
tokens. So it's like a you have a
9:12
concept like the ruins of an ancient
9:14
civilization stand as a testament to a
9:15
bygone era. They're intricate and then
9:17
it cuts off the tokens and then creates
9:19
a new idea based off of all of these
9:21
previous ideas, right? Right. And so the
9:22
new idea for in this instance would be
9:25
paints the landscape in a symphony of
9:26
hues from vibrant yellows and oranges to
9:29
deep greens and blues. Animals in
9:31
harmony with nature adorning the flora
9:33
with dazzling feathers, colorful scales
9:35
and intricate patterns. And then it kind
9:37
of iterates from here, right? We get
9:39
multiple iterations of it going through.
9:41
So we get iteration two. Uh and then so
9:44
from there we get more ideas, right? So
9:46
at birth, children are given a
9:47
problem-solving blueprint. And then as
9:50
you emerge from the castle's ruins, you
9:52
hear the quiet murmur of a stream
9:54
winding through the forest undergrowth,
9:56
etc. So it kind of it starts majorly and
9:59
significantly evolving from there,
10:01
right? And then that's kind of the whole
10:04
entire uh concept of what this does,
10:07
right? It explores the latent space,
10:09
explores the the problem vectors within
10:11
the latent space to create unique and
10:14
creative solutions uh within it overall.
10:16
And that's kind of what this overall
10:18
framework does, what we're looking at
10:20
here and what this research paper kind
10:22
of proves out. So it's it's interesting
10:24
to me again overall cuz it's uh this is
10:26
a concept that I've been talking about
10:28
for a long time and for a long while
10:29
now. I just talk about it very
10:32
specifically as it relates to swarm
10:33
algorithms because I think that like
10:34
I've swarm algorithms are the best
10:37
mechanism in order to explore this
10:39
latent space but you can absolutely
10:41
combine that with LM models as I've
10:43
demonstrated here and then so I'll leave
10:44
a link to all of this uh both the collab
10:46
notebook as well as the research paper
10:48
here uh and if you like this type of
10:49
content please like and subscribe thank
10:51
you
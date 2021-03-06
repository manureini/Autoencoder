#
#  This script uses the MNIST Handwritten Digit Dataset and an Autoencoder
#  to recreate the given input image with "encoding_dim" neurons between encoder and decoder
#  It needs a cuda supported environment
#  If you want to use this script in google colab select Runtime GPU paste this script and press run ;)
#

import torch.nn as nn
import torch
import torchvision.transforms as transforms
from torchvision import datasets
import matplotlib.pyplot as plt
import numpy as np


PATH = './sim_autoencoder.pth'

transform = transforms.Compose([
    transforms.ToTensor()
])

# load the training and test datasets
train_data = datasets.MNIST(root='data', train=True,
                                   download=True, transform=transform)
test_data = datasets.MNIST(root='data', train=False,
                                  download=True, transform=transform)
								  
# Create training and test dataloaders

# how many samples per batch to load
batch_size = 32

#Amount of neurons in middle hidden layer
encoding_dim = 3

# prepare data loaders
train_loader = torch.utils.data.DataLoader(train_data, batch_size=batch_size, num_workers=0, pin_memory=True, shuffle=True)
test_loader = torch.utils.data.DataLoader(test_data, batch_size=batch_size, num_workers=0, pin_memory=True, shuffle=True)

# define the NN architecture
class Autoencoder(nn.Module):
    def __init__(self, encoding_dim):
        super(Autoencoder, self).__init__()
        ## encoder ##
        # linear layer (784 -> encoding_dim)
        self.encoder = nn.Sequential(
            nn.Linear(28 * 28, 256),
            nn.ReLU(True),
            nn.Linear(256, encoding_dim),
            nn.ReLU(True))
         
        ## decoder ##
        # linear layer (encoding_dim -> input size)
        self.decoder = nn.Sequential(
            nn.Linear(encoding_dim, 256),
            nn.ReLU(True),
            nn.Linear(256, 28 * 28),
            nn.Sigmoid())
        

    def forward(self, x):
        # add layer, with relu activation function
        x = self.encoder(x)
        # output layer (sigmoid for scaling from 0 to 1)
        x = self.decoder(x)
        return x

# initialize the NN
model = Autoencoder(encoding_dim)
print(model)


#if path.exists(PATH):
#    model.load_state_dict(torch.load(PATH))
#    model.eval()

model = model.to("cuda")

# specify loss function
criterion = nn.BCELoss()

# specify loss function
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

lossfile = open("loss.txt","w+")

n_epochloops = 2;

for epochLoops in range(0, n_epochloops):
    n_epochs = 5
    
    for epoch in range(1, n_epochs+1):
        # monitor training loss
        train_loss = 0.0
        
        ###################
        # train the model #
        ###################
        for data in train_loader:
            # _ stands in for labels, here
            images, _ = data
            
            images = images.to("cuda");
            
            #flatten images
            images = images.view(images.size(0), -1)
            
            # clear the gradients of all optimized variables
            optimizer.zero_grad()        
            
            # forward pass: compute predicted outputs by passing inputs to the model
            outputs = model(images)
            
            # calculate the loss
            loss = criterion(outputs, images)
            
            # backward pass: compute gradient of the loss with respect to model parameters
            loss.backward()
            
            # perform a single optimization step (parameter update)
            optimizer.step()           
        
            # update running training loss
            train_loss += loss.item()*images.size(0)
            
        # print avg training statistics 
        train_loss = train_loss/len(train_loader)
        
        realEpoch = epoch + (epochLoops * n_epochs)
        
        print('Epoch: {} \tTraining Loss: {:.6f}'.format(
            realEpoch, 
            train_loss
            ))
        lossfile.write("%d;%f\n" % (realEpoch,train_loss))
        lossfile.flush()
        
    		
    # obtain one batch of test images
    dataiter = iter(test_loader)
    images, labels = dataiter.next()
    
    images_flatten = images.view(images.size(0), -1)
    # get sample outputs
    output = model(images_flatten.cuda()).cpu()
    # prep images for display
    images = images.numpy()
    
    # output is resized into a batch of images
    output = output.view(batch_size, 1, 28, 28)
    
    # use detach when it's an output that requires_grad
    output = output.detach().numpy()
    
    # plot the first ten input images and then reconstructed images
    fig, axes = plt.subplots(nrows=2, ncols=10, sharex=True, sharey=True, figsize=(25,4))
    
    # input images on top row, reconstructions on bottom
    for images, row in zip([images, output], axes):
        for img, ax in zip(images, row):
            ax.imshow(np.squeeze(img), cmap='gray')
            ax.get_xaxis().set_visible(False)
            ax.get_yaxis().set_visible(False)
    
    
    torch.save(model.state_dict(), PATH)


lossfile.close()
print("done!")




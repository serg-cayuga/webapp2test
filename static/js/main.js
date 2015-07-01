angular.module('webApp')
    .controller('MainController', function ($scope, $http, authUser, UserService, UserResource, MessagesResource) {
        $scope.authUser = authUser;
        $scope.logout = function(){
            UserService.logout();
        };

        $scope.users = UserResource.query();
        $scope.currentUser;
        $scope.messageText = '';
        $scope.sendError = '';
        $scope.messages = [];

        $scope.users.$promise.then(function(users){
            if (users) {
                $scope.currentUser = users[0].key;
                $scope.messages =  MessagesResource.query({id: $scope.currentUser});
            }
        });

        $scope.viewMessages = function (userId) {
            $scope.currentUser = userId;
            $scope.messages =  MessagesResource.query({id: $scope.currentUser});
        };

        $scope.sendMessage = function () {
            if (!$scope.messageText) return;
            var newMessage = new MessagesResource({'text': $scope.messageText});
            newMessage.$send({id: $scope.currentUser}, function(data) {
                $scope.messageText = '';
                $scope.messages.splice(0, 0, data);
            }, function(error) {
                $scope.sendError = "Message sending error. Try again please.";
            });
        };

    });

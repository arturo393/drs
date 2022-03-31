/* eslint-disable */
/* glean-disable */

function getData() {
  var graphData = {};
  var errors = {};
  var positionData;

  processData = (response) => {
    graphData[response['type']] = response['data'];

    // console.log(graphData)
  };

  processError = (error) => {
    // errors[error['type']] = error['data']
    throw error;
  };

  var hostPromise = getHosts().then(processData, processError);
  var servicePromise = getServices().then(processData, processError);
  var dependencyPromise = getDependencies().then(processData, processError);
  var positionPromise = getNodePositions().then(processData, processError);
  var settingsPromise = getSettings().then(processData, processError);

  Promise.all([
    hostPromise,
    servicePromise,
    dependencyPromise,
    positionPromise,
    settingsPromise,
  ])
    .then(() => {
      if (window.location.href.indexOf('Fullscreen') > -1) {
        var isFullscreen = true;
        $('.fabs').hide();
      } else {
        var isFullscreen = false;
      }

      if (window.location.href.indexOf('hierarchy') > -1) {
        var isHierarchical = true;
        $('.fabs').hide();
      } else {
        var isHierarchical = false;
      }

      // console.log(graphData.dependencies['results'].length)
      // console.log(graphData.dependencies['results'].length === true)
      // if (!graphData.dependencies['results'].length) {
      //     // if (graphData.hosts['results'].length) {
      //     //     console.log(graphData.hosts['results'].length)
      //     //     throw {
      //     //         type: 'configuration',
      //     //         message: 'Settings are preventing any hosts from being displayed, please enable showing hosts with no dependencies'
      //     //     }
      //     // }
      // }

      formatDependencies(
        graphData.hosts,
        graphData.services,
        graphData.dependencies,
        isHierarchical,
        graphData.positions,
        isFullscreen,
        graphData.settings
      );
    })
    .catch((errors) => {
      errorHandler(errors);
    });
}

function formatDependencies(
  hostData,
  serviceData,
  dependencyData,
  isHierarchical,
  positionData,
  isFullscreen,
  settings
) {
  //Function takes host state data, dependency data, and position data and builds a vis.js usable object using
  //the HostArray and Host objects. Neccesary due to needing match hosts with passed dependencies.

  var Hosts = new HostArray();

  //Start Patch
  console.log('Start Patch...');
  // hostData.results.push(...serviceData.results);
  // console.log('Format Dependencies');
  // console.log('===================');
  // console.log('hostData:');
  // console.log(hostData.results);
  // console.log('serviceData:');
  // console.log(serviceData.results);
  // console.log('dependencyData:');
  // console.log(dependencyData.results);

  console.log("=====HOSTS======");
  hostData.results.map(host => {
    if (host.attrs.vars?.addToMap === false) return false;
    Hosts.addHost(host.attrs);
    // Parent Hosts
    if (typeof host.attrs.vars?.parents !== 'undefined' && host.attrs.vars?.parents !== null) {
      host.attrs.vars?.parents.map(parent => {
        Hosts.addDependency({
          parent_host_name: parent,
          child_host_name: host.attrs.name,
        });
      })
      }
    serviceData.results.map(service => {
      if (service.attrs.host_name === host.attrs.name) {
	const serviceId = service.attrs.name;
        service.attrs.name = service.attrs.host_name+"-"+service.attrs.name;
        Hosts.addHost({ ...service.attrs, id: serviceId, type: 'Service' });
        Hosts.addDependency({
              parent_host_name: service.attrs.host_name,
              child_host_name: service.attrs.name,
            });
        if (service.attrs.vars?.isOPTPort === true) { 
          try {
            var servicePData = service.attrs.last_check_result.performance_data;
            var performance_data = servicePData.find((val) => val.startsWith('value=')).split('=');
            var values = performance_data[1].split(';');
            var rdus = parseInt(values[0].replace(/[a-z][A-Z]*/g, '') * 1); 
            // var rdus = Math.floor(Math.random() * 10);
            for (k = 0; k < rdus; k++) {
              var hostname = service.attrs.host_name;
              var druGroup = service.attrs.name+"-dru"+eval(k+1)
              var state = 2;
              let parentItem = (k === 0)? service.attrs.name : service.attrs.name + '-dru' + (k);
              let currentItem = service.attrs.name + '-dru' + eval(k+1);

	      var state = 2;
              for (l = 0; l < hostData.results.length; l++) {
                if (druGroup === hostData.results[l].attrs.name) {
                  state = hostData.results[l].attrs.last_check_result.state;
                }
              }  

              Hosts.addHost({
                display_name: "Remote "+eval(k+1),
                name: currentItem,
                state: state,
                hostname: hostname,
                zone: service.attrs.zone,
                druHost: service.attrs.host_name,
                druService: service.attrs.name,
                druGroup: druGroup,
                type: 'None',
              });
              Hosts.addDependency({
                parent_host_name: parentItem,
                child_host_name: currentItem,
              });

            }
          } catch (error) {
            console.log(error);
          }
        }
      }
      
      // if (service.attrs.vars?.isOPTPort === true) { 
      //   //Obtiene la cantidad de DRUs conectados
      //   try {
      //     var servicePData = service.attrs.last_check_result.performance_data;
      //     var performance_data = servicePData.find((val) => val.startsWith('value=')).split('=');
      //     var values = performance_data[1].split(';');
      //     var rdus = parseInt(values[0].replace(/[a-z][A-Z]*/g, '') * 1); 
      //     rdus = Math.floor(Math.random() * 10);
      //   } catch (error) {
      //     console.log(error);
      //   }
      //   //Agrega tantos DRU como Host como cantidad encontrada en el servicio
      //   console.log(k)
      //   // for (k = 0; k < rdus; k++) {
      //   //   var druGroup = serviceData.results[i].attrs.host_name+"-"+serviceData.results[i].attrs.name+"-dru"+eval(k+1)
      //   //   var state = 2;
      //   //   let parentItem = (k === 0)? serviceData.results[i].attrs.name : i + '-' + (k);
      //   //   let currentItem = i + '-' + eval(k+1);
      //   //   Hosts.addHost({
      //   //     display_name: "Remote "+eval(k+1),
      //   //     name: currentItem,
      //   //     state: state,
      //   //     hostname: hostname,
      //   //     zone: serviceData.results[i].attrs.zone,
      //   //     druHost: serviceData.results[i].attrs.host_name,
      //   //     druService: serviceData.results[i].attrs.name,
      //   //     druGroup: druGroup,
      //   //     type: 'None',
      //   //   });
      //   // }

      // }
    })
  })

  // console.log("=====Services======")
  // serviceData.results.map(service => {
  //   if (service.attrs.vars?.addToMap === false) return false;
  //   Hosts.addHost({ ...service.attrs, type: 'Service' });
  //   Hosts.addDependency({
  //     parent_host_name: service.attrs.host_name,
  //     child_host_name: service.attrs.name,
  //   });
  //   // Find RDUs
  //   var serviceVars = service.attrs.vars
  //   if ('isOPTPort' in serviceVars && service.attrs.vars.isOPTPort === true) {
  //     try {
  //       var servicePData = service.attrs.last_check_result.performance_data;
  //       var performance_data = servicePData.find((val) => val.startsWith('value=')).split('=');
  //       var values = performance_data[1].split(';');
  //       var rdus = parseInt(values[0].replace(/[a-z][A-Z]*/g, '') * 1); 
  //     } catch (error) {
  //       console.log(error);
  //     } 
  //   }

  // })


  // Add hosts and dependencies only from host data, not from dependencyData
  // for (i = 0; i < hostData.results.length; i++) {
  //   if (hostData.results[i].attrs.vars?.addToMap === false) continue;

  //   Hosts.addHost(hostData.results[i].attrs);
  //   if (
  //     typeof hostData.results[i].attrs.vars?.parents !== 'undefined' &&
  //     hostData.results[i].attrs.vars?.parents !== null
  //   ) {
  //     for (j = 0; j < hostData.results[i].attrs.vars?.parents.length; j++) {
  //       Hosts.addDependency({
  //         parent_host_name: hostData.results[i].attrs.vars?.parents[j],
  //         child_host_name: hostData.results[i].attrs.name,
  //       });
  //     }
  //   }
  // }
  // Add services as hosts
  console.log('Add services as hosts');
  // for (i = 0; i < serviceData.results.length; i++) {
  //   if (serviceData.results[i].attrs.vars?.addToMap === false) continue;

  //   var hostname = serviceData.results[i].attrs.host_name;

  //   Hosts.addHost({ ...serviceData.results[i].attrs, type: 'Service' });
  //   Hosts.addDependency({
  //     parent_host_name: serviceData.results[i].attrs.host_name,
  //     child_host_name: serviceData.results[i].attrs.name,
  //   });

  //   // Add RDUs
  //   //For each MDU Port add RDUs
  //   // if service template contains MDU and is RDU Port
  //   // get rdus connected from attrs.vars.performance_data value (output of check_rs485)
  //   // Add each as Host and dependency
  //   try {
  //     var serviceVars = serviceData.results[i].attrs.vars;
  //     if (serviceVars) {
  //       if (
  //         'isOPTPort' in serviceVars &&
  //         serviceData.results[i].attrs.vars.isOPTPort === true
  //       ) {

  //         try {
  //           var servicePData =
  //             serviceData.results[i].attrs.last_check_result.performance_data;
  //           var performance_data = servicePData
  //             .find((val) => val.startsWith('value='))
  //             .split('=');
  //           var values = performance_data[1].split(';');
  //           var rdus = parseInt(values[0].replace(/[a-z][A-Z]*/g, '') * 1);
  //         } catch (error) {
  //           console.log(error);
  //         }         

  //         // Add RDUs as Hosts
  //         console.log('Add rdus as hosts');
  //         for (k = 0; k < rdus; k++) {
  //           // Calculate ServiceGroup Link
  //           // Format: dmu1-opt1-dru1
  //           // dmu1 part from host of this service
  //           // opt1 part from the name of this service
  //           // dru1 part from this index (i)
  //           var druGroup = serviceData.results[i].attrs.host_name+"-"+serviceData.results[i].attrs.name+"-dru"+eval(k+1)

	//    var state = 2;
  //          for (l = 0; l < hostData.results.length; l++) {
  //             if (druGroup === hostData.results[l].attrs.name) {
	// 	   state = hostData.results[l].attrs.last_check_result.state;
	// 		}
  //           } 

  //           let parentItem =
  //             k === 0 ? serviceData.results[i].attrs.name : i + '-' + (k);
  //           let currentItem = i + '-' + eval(k+1);
  //           Hosts.addHost({
  //             display_name: "Remote "+eval(k+1),
  //             name: currentItem,
  //             state: state,
  //             hostname: hostname,
  //             zone: serviceData.results[i].attrs.zone,
  //             druHost: serviceData.results[i].attrs.host_name,
  //             druService: serviceData.results[i].attrs.name,
  //             druGroup: druGroup,
  //             type: 'None',
  //           });
  //           Hosts.addDependency({
  //             parent_host_name: parentItem,
  //             child_host_name: currentItem,
  //           });
  //         }
  //       }
  //     }
  //   } catch (e) {
  //     console.log(e);
  //   }
  // }
  console.log('End Patch');
  // END Patch

  //   for (i = 0; i < hostData.results.length; i++) {
  //     Hosts.addHost(hostData.results[i].attrs);
  //   }

  //   for (i = 0; i < dependencyData.results.length; i++) {
  //     Hosts.addDependency(dependencyData.results[i].attrs);
  //   }

  if (positionData) {
    for (i = 0; i < positionData.length; i++) {
      Hosts.addPosition(positionData[i]);
    }
  }

  drawNetwork(Hosts, isHierarchical, isFullscreen, settings);
}

function drawNetwork(Hosts, isHierarchical, isFullscreen, settings) {
  //function uses data provided by the 'Hosts' and 'settings' objects to draw a vis.js network
  //In accordance with passed settings and data.

  var color_border = 'yellow';

  var newHost = false; //is true when a host is present with no positon data.

  color_background = 'white';

  var nodes = new vis.DataSet([]);

  var edges = new vis.DataSet([]);

  for (i = 0; i < Hosts.length; i++) {
    currHost = Object.keys(Hosts.hostObject)[i]; //gets name of current host based on key iter
    if (typeof currHost === 'undefined') {
      continue;
    }

    node_type = Hosts.hostObject[currHost].type;
    node_parent = Hosts.hostObject[currHost].parents[0];
    node_drugroup = Hosts.hostObject[currHost].druGroup;
    node_hostname = Hosts.hostObject[currHost].hostname;
    node_servicename = Hosts.hostObject[currHost].druService;

    if (
      settings.display_only_dependencies &&
      !Hosts.hostObject[currHost].hasDependencies
    ) {
      //skip adding node

      continue;
    }

    //colors based on host state

    if (Hosts.hostObject[currHost].status === 'DOWN') {
      color_border = 'red';

      if (settings.display_down) {
        text_size = settings.text_size / 2; //parse int because an int is returned for MySql, a string for Postgres.
      } else {
        text_size = 0;
      }
    }

    if (Hosts.hostObject[currHost].status === 'UNREACHABLE') {
      color_border = 'purple';

      if (settings.display_unreachable) {
        text_size = settings.text_size / 2;
      } else {
        text_size = 0;
      }
    }

    if (Hosts.hostObject[currHost].status === 'UP') {
      color_border = 'green';

      if (settings.display_up) {
        text_size = settings.text_size / 2;
      } else {
        text_size = 0;
      }
    }

    if (
      settings.always_display_large_labels &&
      Hosts.hostObject[currHost].isLargeNode > 3
    ) {
      text_size = settings.text_size / 2;
    }

    if (settings.alias_only) {
      hostLabel = Hosts.hostObject[currHost].description;
    } else {
      hostLabel =
        Hosts.hostObject[currHost].description + '\n(' + currHost + ')';
    }

    if (Hosts.hostObject[currHost].hasPositionData) {
      nodes.update({
        //vis.js function
        id: currHost,
        type: node_type,
        parent: node_parent,
        label: hostLabel,
        drugroup: node_drugroup,
	hostname: node_hostname,
        servicename: node_servicename,
        mass: Hosts.hostObject[currHost].children.length / 4 + 1,
        color: {
          border: color_border,
          background: color_background,
        },

        font: {
          size: text_size,
        },

        size:
          Hosts.hostObject[currHost].children.length * 3 * settings.scaling +
          20,

        x: Hosts.hostObject[currHost].position.x, //set x, y position
        y: Hosts.hostObject[currHost].position.y,
      });
    } else {
      newHost = true; //has no position data, newly added

      nodes.update({
        id: currHost,
        type: node_type,
        parent: node_parent,
        label: hostLabel,
        drugroup: node_drugroup,
        mass: Hosts.hostObject[currHost].children.length / 4 + 1,
        color: {
          border: color_border,
          background: color_background,
        },

        font: {
          size: text_size,
        },

        size:
          Hosts.hostObject[currHost].children.length * 3 * settings.scaling +
          20,
      });
    }

    for (y = 0; y < Hosts.hostObject[currHost].parents.length; y++) {
      edges.update({
        from: Hosts.hostObject[currHost].parents[y],
        to: currHost,
      });
    }
  }

  var networkData = {
    nodes: nodes,
    edges: edges,
  };

  var container = document.getElementById('dependency-network');

  const hierarchyOptions = {
    layout: {
      hierarchical: {
        enabled: true,
        levelSeparation: 200,
        nodeSpacing: 150,
        treeSpacing: 200,
        blockShifting: true,
        edgeMinimization: true,
        parentCentralization: true,
        direction: 'LR',
        sortMethod: 'directed',
      },
    },
    edges: {
      arrows: {
        middle: {
          enabled: true,
          scaleFactor: 1,
          type: 'arrow',
        },
      },
    },
    nodes: {
      shape: 'square',
      fixed: true,
      scaling: {
        min: 1,
        max: 15,
        label: {
          enabled: true,
          min: 14,
          max: 30,
          maxVisible: 30,
          drawThreshold: 5,
        },
      },
    },
  };

  const networkOptions = {
    layout: {
      improvedLayout: false,
      randomSeed: 728804,
    },
    edges: {
      smooth: {
        forceDirection: 'none',
      },
    },

    nodes: {
      scaling: {
        label: true,
      },
      fixed: true,
      shape: 'dot',
    },
  };

  if (isHierarchical) {
    //display using hierarchyOptions
    var network = new vis.Network(container, networkData, hierarchyOptions);
    var draw_type = 'hierarchy';
  } else if (isFullscreen) {
    //display using fullscreen (auto refresh)

    fullscreenMode(container, networkData);

    return;
  } else {
    var network = new vis.Network(container, networkData, networkOptions);

    if (Hosts.isNewNetwork) {
      simulateNewNetwork(network, nodes); //if there is no position data for the network, simulate network.
    } else if (newHost && !isHierarchical) {
      //if a new host was added, and it is not being displayed in hierarchical layout

      simulateChangedNetwork(network, nodes);
    }
  }
  startEventListeners(network, networkData, settings, draw_type);
}

function simulateNewNetwork(network, nodes) {
  //simulates new network with a full number of physics iterations, neccecsary to layout an entire new network
  //somewhat accurately. Automatically saves position upon finishing simulation.

  network.setOptions({
    nodes: {
      fixed: false, //unlock nodes for physics sim
    },
  });

  $('.fabs').hide();

  $('#loadingBar').css('display', 'block');

  $('#notifications')
    .append()
    .html('<li class="info fade-out">Simulating New Network</li>');

  network.on('stabilizationProgress', function (params) {
    //as network is simulating animate by percentage of physics iter complete
    var maxWidth = 496;
    var minWidth = 20;
    var widthFactor = params.iterations / params.total;
    var width = Math.max(minWidth, maxWidth * widthFactor);
    $('#bar').css('width', width);
    $('#text').html(Math.round(widthFactor * 100) + '%');
  });

  network.once('stabilizationIterationsDone', function () {
    $('#text').html('100%');
    $('#bar').css('width', '496');
    $('#loadingBar').css('opacity', '0');
    // really clean the dom element
    setTimeout(function () {
      $('#loadingBar').css('display', 'none');
    }, 500);
    $('.fabs').show();

    network.storePositions(); //visjs function that adds X, Y coordinates of all nodes to the visjs node dataset that was used to draw the network.

    success = () => {
      network.setOptions({
        nodes: {
          fixed: true,
        },
      });
    };

    error = (error) => {
      errorHandler(error);
    };

    var promise = storeNodePositions(nodes._data).then(success, error);
  });
}

function simulateChangedNetwork(network, nodes) {
  //function simulates the network for a limited number of physics iterations,
  //usually enough to correctly place a newly added host/hosts.

  $('#notifications')
    .append()
    .html('<li class="info">Network Change Detected</li>');

  network.setOptions({
    nodes: {
      fixed: false, //unlock nodes
    },
  });

  network.startSimulation(); //start new physics sim
  network.stabilize(800); //on sim for 200 iters, usually enough for the node to place itself automatically.
  network.once('stabilizationIterationsDone', function () {
    network.stopSimulation();
    network.setOptions({
      nodes: {
        fixed: true,
      },
    });
    network.storePositions(); //after new node added, resave network positions

    var promise = storeNodePositions(nodes._data).then(success, error);

    success = () => {
      $('#notification')
        .html(
          '<div class = notification-content><h3>Network Change Detected</h3>'
        )
        .css({
          display: 'block',
        })
        .delay(5000)
        .fadeOut();
    };

    error = (error) => {
      errorHandler(error);
    };
  });
}

function startEventListeners(
  network,
  networkData,
  settings,
  draw_type = 'network'
) {
  var font_size = 0;

  // function launches all event listeners for the network, and buttons.
  let nodes_defs = networkData.nodes._data;

  network.on('doubleClick', function (params) {
    thisNode = nodes_defs[params.nodes[0]];


    //double click on node listener
    if (params.nodes[0] != undefined) {
      $('.fabs').hide();

      let hostMonitoringAddress = '';

      if (thisNode.type === 'Host') {
        if (location.href.indexOf('/icingaweb2') > 1) {
          hostMonitoringAddress = '/icingaweb2/monitoring/host/show?host=';
        } else {
          hostMonitoringAddress = '/monitoring/host/show?host=';
        }

        location.href =
          './network_maps/module/' +
          draw_type +
          '#!' +
          hostMonitoringAddress +
          params.nodes[0]; //redirect to host info page.
      } else if (thisNode.type === 'Service') {
        if (location.href.indexOf('/icingaweb2') > 1) {
          hostMonitoringAddress = '/icingaweb2/monitoring/service/show?host=';
        } else {
          hostMonitoringAddress = '/monitoring/service/show?host=';
        }
	
        location.href =
          './network_maps/module/' +
          draw_type +
          '#!' +
          hostMonitoringAddress +
          thisNode.parent +
          '&service=' +
          params.nodes[0].split('-')[1];
  //        params.nodes[0]; //redirect to host info page.
      } else if (thisNode.type === 'None') {
       

	 ///monitoring/host/services?host=dmu1&service=OPT3
        if (location.href.indexOf('/icingaweb2') > 1) {
          hostMonitoringAddress = '/icingaweb2/monitoring/host/show?host=';
        } else {
          hostMonitoringAddress = '/monitoring/host/show?host=';
        }

        location.href =
          './network_maps/module/' +
          draw_type +
          '#!' +
          hostMonitoringAddress +
          thisNode.drugroup;

        
      }
    }
  });

  network.on('selectNode', function (params) {
    //on selecting node, background of label is made solid white for readabillity.
    var clickedNode = network.body.nodes[params.nodes[0]];
    font_size = clickedNode.options.font.size;
    clickedNode.setOptions({
      font: {
        size: 30,
        background: 'white',
      },
    });
  });

  network.on('deselectNode', function (params) {
    //on node deselect, label set back to transparent.

    var clickedNode = network.body.nodes[params.previousSelection.nodes[0]];
    clickedNode.setOptions({
      font: {
        size: font_size,
        background: 'none',
      },
    });
  });

  $('#edit-btn').click(function (params) {
    //on edit

    $('#notifications')
      .append()
      .html('<li class="info">Editing Node Positions</li>');

    network.setOptions({
      //unlock nodes for editing
      nodes: {
        fixed: false,
      },
    });

    $('.edit-fab').toggleClass('scale-out'); // show secondary FABs
    if ($('.edit-fab').hasClass('scale-out')) {
      //if already scaled out, second click hides secondary FABs and locks nodes
      network.setOptions({
        nodes: {
          fixed: true,
        },
      });
    }
  });

  $('#edit-btn-delete').click(function () {
    if (confirm('Reset All Network Positions?')) {
      success = () => {
        setTimeout(function () {
          window.location.replace('./network'); //on succes redirect to network.
        }, 2000);
      };

      error = (error) => {
        errorHandler(error);
      };

      var promise = storeNodePositions('RESET').then(success, error);
    }
  });

  $('#edit-btn-save').click(function () {
    //on save

    network.setOptions({
      nodes: {
        fixed: true,
      },
    });

    network.storePositions(); //visjs function that adds X, Y coordinates of all nodes to the visjs node dataset that was used to draw the network.

    success = () => {
      $('#notifications')
        .append()
        .html('<li class="success fade-out">Nodes Positions Saved</li>');
    };

    error = (error) => {
      errorHandler(error);
    };

    var promise = storeNodePositions(networkData.nodes._data).then(
      success,
      error
    );
  });

  $('#edit-btn-fullscreen').click(() => {
    if (settings.fullscreen_mode === 'network') {
      window.location.replace('./network_maps/module/network?showFullscreen');
    } else {
      window.location.replace(
        './network_maps/module/statusGrid?showFullscreen'
      );
    }
  });

  if (settings['enable_director'] === true) {
    $('#dependency-fabs').show();

    $('#dependency-btn').click(() => {
      network.setOptions({
        nodes: {
          fixed: false,
        },
      });

      $('.dependency-fab').toggleClass('scale-out'); // show secondary FABs

      if (!$('.edit-fab').hasClass('scale-out')) {
        //if already scaled out, second click hides secondary FABs and locks nodes
        $('.edit-fab').toggleClass('scale-out');
      }

      $('#notifications')
        .append()
        .html('<li class="info">Editing Dependencies</li>');

      if (!settings.default_dependency_template) {
        alert(
          'No Default Director Dependency Template Selected, Please Create or Select One.'
        );
        window.location.replace('./settings');
      }

      $('#notification')
        .html(
          '<div class = notification-content><h3>Editing Dependencies (Child -----> Parent)</h3>'
        )
        .css({
          display: 'block',
        });

      network.setOptions({
        edges: {
          arrows: {
            from: true,
          },
        },
      });

      network.off('doubleClick');

      network.off('selectNode');

      network.off('deselectNode');

      $('#dependency-btn').off();

      $('#edit-btn').off();

      startDependencyModeListeners(networkData, network, settings);
    });
  }
}

function startDependencyModeListeners(networkData, network, settings) {
  var dependencies = [];

  var dependency = [];

  var updatedNodes = [];

  var container = document.getElementById('dependency-network');

  network.on('selectNode', function (params) {
    //on selecting node, background of label is made solid white for readabillity.

    var selectedNode = network.body.nodes[params.nodes[0]];

    dependency.push(selectedNode.id);

    if (dependency.length === 2) {
      drawnDependency = {
        object_name: dependency[0] + ' __to__ ' + dependency[1],
        object_type: 'apply',
        assign_filter: 'host.name=%22' + dependency[0] + '%22',
        imports: [settings.default_dependency_template],
        apply_to: 'host',
        parent_host: dependency[1],
      };

      networkData.edges.update({
        id: drawnDependency.object_name,
        from: dependency[1],
        to: dependency[0],
      });

      dependencies.push(drawnDependency);

      dependency = [];
    }
  });

  network.on('click', function (params) {
    if (params.nodes[0] === undefined) {
      dependency = [];
    }
  });

  $('#dependency-btn').click(() => {
    $('.dependency-fab').toggleClass('scale-out'); // show secondary FABs
    if ($('.dependency-fab').hasClass('scale-out')) {
      //if already scaled out, second click hides secondary FABs and locks nodes
      network.setOptions({
        nodes: {
          fixed: true,
        },
        edges: {
          arrows: {
            from: false,
          },
        },
      });
    }

    network.off('doubleClick');

    network.off('selectNode');

    network.off('deselectNode');

    $('#dependency-btn').off();

    startEventListeners(network, networkData, settings);
  });

  $('#edit-btn').click(() => {
    $('#notifications')
      .append()
      .html('<li class="info">Editing Node Positions</li>');

    $('.dependency-fab').toggleClass('scale-out');
    network.setOptions({
      nodes: {
        fixed: false,
      },
      edges: {
        arrows: {
          from: false,
        },
      },
    });

    $('.edit-fab').toggleClass('scale-out');

    network.off('doubleClick');

    network.off('selectNode');

    network.off('deselectNode');

    $('#dependency-btn').off();
    $('#edit-btn').off();

    startEventListeners(network, networkData, settings);
  });

  $('#dependency-btn-undo').click(() => {
    if (dependencies.length === 0) {
      alert('Nothing to Undo');
      return;
    }

    removedDependency = dependencies.pop();

    networkData.edges.remove({
      id: removedDependency.object_name,
    });
  });

  $('#dependency-btn-save').click(function () {
    //on save

    importDependencies(dependencies);

    network.storePositions(); //visjs function that adds X, Y coordinates of all nodes to the visjs node dataset that was used to draw the network.

    $.ajax({
      //ajax request to store into DB
      url: './network_maps/module/storeNodePositions',
      type: 'POST',
      data: {
        json: JSON.stringify(networkData.nodes._data),
      },
    });
  });
}

function importDependencies(dependencies) {
  for (i = 0; i < dependencies.length; i++) {
    $.ajax({
      url: './director/dependency',
      type: 'POST',
      headers: {
        Accept: 'application/json',
      },
      data: JSON.stringify(dependencies[i]),
      success: () => {
        deployChanges();
      },
      error: function (data) {
        console.log(data);
        alert(
          'Adding dependency Unsuccessful:\n\n' + data.responseJSON['message']
        );
        return;
      },
    });
  }
}

function deployChanges() {
  $.ajax({
    url: './director/config/deploy',
    type: 'POST',
    headers: {
      Accept: 'application/json',
    },
    success: function (data) {
      $('#notifications')
        .append()
        .html(
          '<li class="success fade-out">Dependencies Saved Successfully</li>'
        );
    },
  });
}

function Host(hostData) {
  //function accepts raw host data pulled from icinga 2 api, and formats it into a more usable format
  //while providing functions to add dependencies and position

  determineStatus = (state, wasReachable) => {
    if (state === 0) {
      return 'UP';
    } else if (state === 1 && !wasReachable) {
      return 'UNREACHABLE';
    } else {
      return 'DOWN';
    }
  };

  this.name = '' || hostData.name;
  this.status = determineStatus(hostData.state, hostData.last_reachable);
  this.description = '' || hostData.display_name;
  this.druHost = '' || hostData.druHost;
  this.hostname = '' || hostData.hostname;
  this.druService = '' || hostData.druService;
  this.druGroup = '' || hostData.druGroup;
  this.type = '' || hostData.type;
  this.hasDependencies = false;
  this.parents = [];
  this.isLargeNode = false;
  this.group = '' || hostData.groups;
  this.children = [];
  this.position = {
    x: 0,
    y: 0,
  };
  this.hasPositionData = false;

  this.addParent = (parent) => {
    this.parents.push(parent);
    this.hasDependencies = true;
  };

  this.addChild = (Child) => {
    this.children.push(Child);
    this.hasDependencies = true;

    if (this.children.length > 3) {
      this.isLargeNode = true;
    }
  };

  this.setPositionData = (data) => {
    this.position.x = data.node_x;
    this.position.y = data.node_y;
    this.hasPositionData = true;
  };
}

function HostArray() {
  this.hostObject = {};

  this.isNewNetwork = true; //if there any node has position data

  this.length = 0;

  this.addHost = (hostData) => {
    this.hostObject[hostData.name] = new Host(hostData);

    this.length++;
  };

  this.addDependency = (dependency) => {
    childName = dependency.child_host_name;

    parentName = dependency.parent_host_name;

    if (isInHosts(parentName)) {
      this.hostObject[parentName].addChild(childName);
    }

    if (isInHosts(childName)) {
      this.hostObject[childName].addParent(parentName);
    }
  };

  this.addPosition = (positionData) => {
    name = positionData.node_name;

    if (isInHosts(name)) {
      this.hostObject[name].setPositionData(positionData);

      this.isNewNetwork = false;
    }
  };

  isInHosts = (name) => {
    return this.hostObject[name] != undefined;
  };
}



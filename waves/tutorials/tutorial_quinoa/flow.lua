inciter = {

  title = "Flow in a simple box" ,

  term = 0.11,  -- Max physical time, s
  ttyi= 10,  -- TTY output interval
  cfl =0.8,
  scheme = "alecg",

  partitioning = "rcb",

  compflow = {
    physics ="euler", 
  },
    -- Units: m,kg,s,
  ic = {
    density = 0.912,  -- kg/m^3
    velocity={ 0.0, 0.0, 0.0 },  -- m/s
    pressure = 77816.5,  -- Initiate linear
  },

  material = {
    {
      gamma = { 1.4 },
      cv ={ 717.5 },
    }
  },

  bc = { 
    {
      farfield = {6},  -- Outlet
      pressure = 77816.5,
      density = 0.912,
      velocity = {0.0, 0.0, 0.0},
      timedep = { 
	{
          sideset = {4}, --Inlet
	  fn = {  -- t  p  rho  xvel yvel zvel
            0.0, 77816.5, 0.912, 0.000, 0.000, 0.000,
            0.1, 77816.5, 0.912, 5.000, 0.000, 0.000,
           10.0, 77816.5, 0.912, 5.000, 0.000, 0.000,
	  }
	}
      },
      symmetry = {1,2,3,5},
    }
  },


  history_output = {
    interval = 1,
    point = {
      {id = "p1", coord = { 0.5, 0.25, 0.25 }},
    }
  },


  field_output = {
    time_interval = 0.001,
    nodevar = {
      "density",
      "x-velocity",
      "y-velocity",
      "z-velocity",
      "specific_total_energy",
      "pressure"
    }
  },
 

  diagnostics = {
    interval= 250,
    format  = "scientific",
    error   =  "l2"
  }

}

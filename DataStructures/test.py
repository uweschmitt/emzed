from TableParser import *
            
     
if __name__ == "__main__":
    
    table = XCMSFeatureParser.parse(file("output_from_xcms.csv").readlines())
    ti    = table.extractColumns("mz", "mzmin", "mzmax")
    ti.addColumn("avgdiff", "@expr", "mz - 0.5*(mzmin+mzmax)")

            
            


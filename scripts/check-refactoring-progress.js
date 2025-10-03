#!/usr/bin/env node

/**
 * Refactoring Progress Checker
 * 
 * Compares actual file structure against design/REFACTORING_PLAN.md
 * Reports missing files, extra files, and migration progress
 */

const fs = require('fs');
const path = require('path');

const PROJECT_ROOT = path.resolve(__dirname, '..');
const DESIGN_FILE = path.join(PROJECT_ROOT, 'design', 'REFACTORING_PLAN.md');

// Expected file structure from design
const EXPECTED_STRUCTURE = {
  'src/server.py': { maxLines: 100, status: 'to-refactor' },
  
  // Resources
  'src/resources/__init__.py': { maxLines: 50, status: 'pending' },
  'src/resources/base.py': { maxLines: 100, status: 'pending' },
  
  'src/resources/project/__init__.py': { maxLines: 50, status: 'pending' },
  'src/resources/project/list.py': { maxLines: 50, status: 'pending' },
  'src/resources/project/get.py': { maxLines: 50, status: 'pending' },
  'src/resources/project/create.py': { maxLines: 50, status: 'pending' },
  'src/resources/project/update.py': { maxLines: 50, status: 'pending' },
  
  'src/resources/item/__init__.py': { maxLines: 50, status: 'pending' },
  'src/resources/item/add.py': { maxLines: 50, status: 'pending' },
  'src/resources/item/remove.py': { maxLines: 50, status: 'pending' },
  'src/resources/item/list.py': { maxLines: 50, status: 'pending' },
  'src/resources/item/update.py': { maxLines: 50, status: 'pending' },
  
  'src/resources/field/__init__.py': { maxLines: 50, status: 'pending' },
  'src/resources/field/get.py': { maxLines: 50, status: 'pending' },
  
  'src/resources/owner/__init__.py': { maxLines: 50, status: 'pending' },
  'src/resources/owner/get_id.py': { maxLines: 50, status: 'pending' },
  
  // GraphQL
  'src/graphql/__init__.py': { maxLines: 50, status: 'pending' },
  'src/graphql/queries/list_projects.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/queries/get_project_details.graphql': { maxLines: 100, status: 'pending' },
  'src/graphql/queries/list_project_items.graphql': { maxLines: 100, status: 'pending' },
  'src/graphql/queries/get_project_fields.graphql': { maxLines: 100, status: 'pending' },
  'src/graphql/queries/get_owner_id.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/mutations/create_project.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/mutations/update_project.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/mutations/add_item.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/mutations/remove_item.graphql': { maxLines: 50, status: 'pending' },
  'src/graphql/mutations/update_field.graphql': { maxLines: 50, status: 'pending' },
  
  // Lib (migrated infrastructure)
  'src/lib/__init__.py': { maxLines: 50, status: 'pending' },
  'src/lib/graphql_client.py': { maxLines: 100, status: 'pending' },
  'src/lib/auth.py': { maxLines: 50, status: 'pending' },
};

function countLines(filePath) {
  try {
    const content = fs.readFileSync(filePath, 'utf8');
    return content.split('\n').length;
  } catch (err) {
    return 0;
  }
}

function checkFileExists(filePath) {
  return fs.existsSync(filePath);
}

function analyzeProgress() {
  console.log('🔍 Checking refactoring progress...\n');
  
  let totalFiles = 0;
  let existingFiles = 0;
  let compliantFiles = 0;
  let violations = [];
  
  for (const [relativePath, spec] of Object.entries(EXPECTED_STRUCTURE)) {
    totalFiles++;
    const fullPath = path.join(PROJECT_ROOT, relativePath);
    const exists = checkFileExists(fullPath);
    
    if (exists) {
      existingFiles++;
      const lineCount = countLines(fullPath);
      
      if (lineCount <= spec.maxLines) {
        compliantFiles++;
        console.log(`✅ ${relativePath} (${lineCount} lines)`);
      } else {
        violations.push({
          file: relativePath,
          actual: lineCount,
          expected: spec.maxLines
        });
        console.log(`⚠️  ${relativePath} (${lineCount} lines, exceeds ${spec.maxLines})`);
      }
    } else {
      console.log(`❌ ${relativePath} (missing)`);
    }
  }
  
  // Check for legacy files that should be removed
  console.log('\n🗑️  Legacy files to remove:');
  const legacyFiles = [
    'src/graphql_client.py',
    'src/auth.py'
  ];
  
  for (const legacyFile of legacyFiles) {
    const fullPath = path.join(PROJECT_ROOT, legacyFile);
    if (checkFileExists(fullPath)) {
      console.log(`⚠️  ${legacyFile} (should be in src/lib/)`);
    } else {
      console.log(`✅ ${legacyFile} (removed)`);
    }
  }
  
  // Summary
  console.log('\n📊 Progress Summary:');
  console.log(`   Total expected files: ${totalFiles}`);
  console.log(`   Files created: ${existingFiles} (${Math.round(existingFiles/totalFiles*100)}%)`);
  console.log(`   Files compliant: ${compliantFiles} (${Math.round(compliantFiles/totalFiles*100)}%)`);
  
  if (violations.length > 0) {
    console.log('\n🚨 Line count violations:');
    for (const v of violations) {
      console.log(`   ${v.file}: ${v.actual} lines (max ${v.expected})`);
    }
  }
  
  // Phase detection
  console.log('\n📍 Current Phase:');
  if (existingFiles === 0) {
    console.log('   Phase 1: Infrastructure Setup (not started)');
  } else if (existingFiles < 10) {
    console.log('   Phase 2-4: GraphQL extraction and base setup (in progress)');
  } else if (existingFiles < 20) {
    console.log('   Phase 5-8: Resource extraction (in progress)');
  } else if (existingFiles < totalFiles) {
    console.log('   Phase 9-11: Finalization (in progress)');
  } else {
    console.log('   Phase 12: Complete! Ready for commit 🎉');
  }
}

analyzeProgress();
